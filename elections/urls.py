from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import CategoryViewSet, CandidateViewSet, VoteViewSet, ElectionResultViewSet, BlockchainViewSet, test_cloudinary, debug_storage
from . import views



router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'candidates', CandidateViewSet)
router.register(r'votes', VoteViewSet, basename="votes")
router.register(r'results', ElectionResultViewSet, basename="results")
router.register(r'blockchain', BlockchainViewSet, basename="blockchain")

urlpatterns = [
    path('', include(router.urls)),
    path('add/', views.add_vote, name='add_vote'),
    path('blocks/', views.view_blocks, name='view_blocks'),
    path('verify/', views.verify_chain, name='verify_chain'),
    path('test-cloudinary/', test_cloudinary),
    path('debug-storage/', debug_storage),
]
