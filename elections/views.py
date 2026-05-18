from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication

from .models import Category, Candidate, Vote, ElectionResult, VoteBlock
from .serializers import (
    CategorySerializer, CandidateSerializer,
    VoteSerializer, ElectionResultSerializer, VoteBlockSerializer
)
from blockchain import VoteBlockchain
from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
import cloudinary
# from .models import VoteBlock
# from .blockchain import VoteBlockchain
import json


def add_vote(request):
    """Test route to add a vote block"""
    vote_data = {
        "voter_id": "123",
        "candidate": "Candidate A"
    }

    block = VoteBlockchain.add_vote_block(vote_data)

    return JsonResponse({
        "message": "Vote added to blockchain",
        "block": block
    })


def view_blocks(request):
    """View all blocks in UI"""
    blocks = VoteBlock.objects.order_by('index')

    formatted_blocks = []
    for b in blocks:
        formatted_blocks.append({
            "index": b.index,
            "timestamp": b.timestamp,
            "data": json.loads(b.data),
            "hash": b.hash,
            "previous_hash": b.previous_hash
        })

    return render(request, "blocks.html", {"blocks": formatted_blocks})


def verify_chain(request):
    """Verify blockchain integrity"""
    is_valid = VoteBlockchain.is_chain_valid()

    return JsonResponse({
        "blockchain_valid": is_valid
    })



# CATEGORY APIs
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


# CANDIDATE APIs
class CandidateViewSet(viewsets.ModelViewSet):
    queryset = Candidate.objects.all()
    serializer_class = CandidateSerializer
    permission_classes = [AllowAny]


# VOTE APIs
class VoteViewSet(viewsets.ModelViewSet):
    serializer_class = VoteSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Vote.objects.filter(voter=self.request.user)

    def create(self, request):
        candidate_id = request.data.get("candidate")

        if not candidate_id:
            return Response(
                {"error": "candidate is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            candidate = Candidate.objects.select_related('category').get(id=candidate_id)
        except Candidate.DoesNotExist:
            return Response(
                {"error": "Candidate not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )

        category = candidate.category
        
        # Check if voting period is active
        from datetime import date
        today = date.today()
        if today < category.start_date:
            return Response(
                {"error": f"Voting has not started yet. Starts on {category.start_date}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if today > category.end_date:
            return Response(
                {"error": f"Voting has ended on {category.end_date}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check: one vote per category per user
        already_voted = Vote.objects.filter(
            voter=request.user,
            candidate__category=category
        ).exists()

        if already_voted:
            return Response(
                {"error": f"You have already voted in the '{category.name}' category."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Record the vote on the blockchain
        vote_data = {
            "voter_id": request.user.id,
            "voter_username": request.user.username,
            "candidate_id": candidate.id,
            "candidate_name": candidate.name,
            "category_id": category.id,
            "category_name": category.name,
        }
        block = VoteBlockchain.add_vote_block(vote_data)

        # Save vote to DB
        vote = Vote.objects.create(
            candidate=candidate,
            voter=request.user,
            block_hash=block["hash"]
        )

        # Update ElectionResult tally (handled by signal now, but keep for redundancy)
        result, created = ElectionResult.objects.get_or_create(
            candidate=candidate,
            category=category,
            defaults={"vote_count": 1}
        )
        if not created:
            result.vote_count += 1
            result.save()

        return Response({
            "status": "vote_cast",
            "candidate": candidate.name,
            "category": category.name,
            "block_hash": block["hash"],
            "block_index": block["index"],
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='check/(?P<category_id>[^/.]+)')
    def check_voted(self, request, category_id=None):
        """Check if the current user has already voted in a given category."""
        voted = Vote.objects.filter(
            voter=request.user,
            candidate__category_id=category_id
        ).exists()
        return Response({"voted": voted})


# ELECTION RESULTS APIs
class ElectionResultViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        """Get all results with proper serialization context"""
        results = ElectionResult.objects.select_related('candidate', 'category').all()
        serializer = ElectionResultSerializer(
            results, 
            many=True,
            context={'request': request}  # Add request context
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='category/(?P<category_id>[^/.]+)')
    def category_results(self, request, category_id=None):
        """Get results for a specific category"""
        results = ElectionResult.objects.select_related(
            'candidate', 'category'
        ).filter(category_id=category_id)
        
        serializer = ElectionResultSerializer(
            results, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='winners')
    def winners(self, request):
        """Get winners from each category (handles ties)"""
        categories = Category.objects.all()
        winners_data = []

        for category in categories:
            # Get results for this category
            results = ElectionResult.objects.filter(category=category)
            
            if not results.exists():
                continue
            
            # Find maximum votes in this category
            max_votes = results.aggregate(max_votes=models.Max('vote_count'))['max_votes']
            
            if max_votes and max_votes > 0:
                # Get all candidates with max votes (handles ties)
                category_winners = results.filter(vote_count=max_votes)
                
                for result in category_winners:
                    winners_data.append({
                        'id': result.id,
                        'category': result.category.id,
                        'category_name': result.category.name,
                        'candidate': result.candidate.id,
                        'candidate_name': result.candidate.name,
                        'vote_count': result.vote_count,
                        'profile_image': request.build_absolute_uri(
                            result.candidate.profile_image.url
                        ) if result.candidate.profile_image else None,
                        'is_tie': category_winners.count() > 1,
                    })

        return Response(winners_data)

    @action(detail=False, methods=['get'], url_path='statistics')
    def statistics(self, request):
        """Get overall voting statistics"""
        total_votes = Vote.objects.count()
        total_candidates = Candidate.objects.count()
        total_categories = Category.objects.count()
        
        # Votes by category
        category_stats = []
        for category in Category.objects.all():
            votes_count = Vote.objects.filter(
                candidate__category=category
            ).count()
            
            category_stats.append({
                'category_id': category.id,
                'category_name': category.name,
                'total_votes': votes_count,
                'candidates_count': category.candidates.count(),
            })

        return Response({
            'total_votes': total_votes,
            'total_candidates': total_candidates,
            'total_categories': total_categories,
            'category_breakdown': category_stats,
            'blockchain_valid': VoteBlockchain.is_chain_valid(),
        })


# BLOCKCHAIN AUDIT APIs
class BlockchainViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        """Return all blocks in the chain."""
        blocks = VoteBlock.objects.order_by('index')
        serializer = VoteBlockSerializer(blocks, many=True)
        return Response({
            "chain_valid": VoteBlockchain.is_chain_valid(),
            "block_count": blocks.count(),
            "blocks": serializer.data,
        })

    @action(detail=False, methods=['get'], url_path='verify')
    def verify(self, request):
        """Simple endpoint to verify chain integrity."""
        valid = VoteBlockchain.is_chain_valid()
        return Response({
            "chain_valid": valid,
            "message": "Blockchain integrity verified." if valid else "WARNING: Chain tampered!"
        })

def test_cloudinary(request):
    """Temporary endpoint to test Cloudinary"""
    try:
        # Check config
        config_check = {
            'storage': settings.DEFAULT_FILE_STORAGE,
            'cloud_name': cloudinary.config().cloud_name,
            'api_key_set': bool(cloudinary.config().api_key),
            'media_url': settings.MEDIA_URL,
        }
        
        # Try test upload
        result = cloudinary.uploader.upload(
            "https://via.placeholder.com/100",
            folder="test"
        )
        
        # Cleanup
        cloudinary.uploader.destroy(result['public_id'])
        
        return JsonResponse({
            'status': 'success',
            'config': config_check,
            'test_upload': result['secure_url'],
            'message': 'Cloudinary is working!'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e),
            'config': config_check
        })