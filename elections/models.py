from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.conf import settings
from cloudinary.models import CloudinaryField


class VoteBlock(models.Model):
    """Blockchain block storage — one row per vote."""
    index = models.IntegerField(unique=True)
    timestamp = models.CharField(max_length=50)
    data = models.TextField()
    previous_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64)

    class Meta:
        ordering = ['index']

    def __str__(self):
        return f"Block #{self.index} — {self.hash[:16]}..."


class Category(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name


class Candidate(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, related_name="candidates", on_delete=models.CASCADE)
    bio = models.TextField()
    policy = models.TextField()
    profile_image = CloudinaryField('image', folder='candidate_images', null=True, blank=True)

    def __str__(self):
        return self.name


class Vote(models.Model):
    candidate = models.ForeignKey(Candidate, related_name="votes", on_delete=models.CASCADE)
    voter = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="votes", on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    block_hash = models.CharField(max_length=64, blank=True)

    # NOTE: No unique_together here — one-vote-per-category is enforced
    # in the view logic (checking if voter already voted in that category).

    def __str__(self):
        return f"{self.voter.username} voted for {self.candidate.name}"


class ElectionResult(models.Model):
    category = models.ForeignKey(Category, related_name="results", on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, related_name="results", on_delete=models.CASCADE)
    vote_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Result for {self.category.name} - {self.candidate.name}"


@receiver(post_save, sender=Vote)
def update_election_results(sender, instance, created, **kwargs):
    """Automatically update election results when a vote is cast"""
    if created:
        result, created = ElectionResult.objects.get_or_create(
            candidate=instance.candidate,
            category=instance.candidate.category,
            defaults={'vote_count': 1}
        )
        if not created:
            result.vote_count += 1
            result.save()