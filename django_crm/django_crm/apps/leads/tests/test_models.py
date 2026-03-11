from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.leads.models import Lead, LeadStatus, LeadSource
from apps.leads.services import LeadService
from apps.leads.selectors import LeadSelector

User = get_user_model()


class LeadModelTest(TestCase):
    """Test Lead model functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.lead_status = LeadStatus.objects.create(
            name='New',
            description='New lead status'
        )
        self.lead_source = LeadSource.objects.create(
            name='Website',
            description='Lead from website'
        )
    
    def test_lead_creation(self):
        """Test lead creation."""
        lead = Lead.objects.create(
            title='Test Lead',
            description='Test description',
            amount=10000,
            currency='USD',
            lead_status_id=self.lead_status.id,
            lead_source_id=self.lead_source.id,
            user_created_id=self.user.id,
            user_owner_id=self.user.id
        )
        
        self.assertEqual(lead.title, 'Test Lead')
        self.assertEqual(lead.amount, 10000)
        self.assertEqual(lead.currency, 'USD')
        self.assertFalse(lead.qualified)
        self.assertIsNone(lead.converted_at)
    
    def test_lead_soft_delete(self):
        """Test lead soft delete."""
        lead = Lead.objects.create(
            title='Test Lead',
            user_created_id=self.user.id,
            user_owner_id=self.user.id
        )
        
        lead.soft_delete(self.user.id)
        lead.refresh_from_db()
        
        self.assertTrue(lead.is_deleted)
        self.assertIsNotNone(lead.deleted_at)
        self.assertEqual(lead.user_deleted_id, self.user.id)
    
    def test_lead_restore(self):
        """Test lead restore."""
        lead = Lead.objects.create(
            title='Test Lead',
            user_created_id=self.user.id,
            user_owner_id=self.user.id
        )
        
        lead.soft_delete(self.user.id)
        lead.restore(self.user.id)
        lead.refresh_from_db()
        
        self.assertFalse(lead.is_deleted)
        self.assertIsNone(lead.deleted_at)
    
    def test_lead_convert_to_deal(self):
        """Test lead conversion to deal."""
        lead = Lead.objects.create(
            title='Test Lead',
            user_created_id=self.user.id,
            user_owner_id=self.user.id
        )
        
        deal = lead.convert_to_deal()
        lead.refresh_from_db()
        
        self.assertIsNotNone(lead.converted_at)
        self.assertEqual(deal.title, lead.title)
        self.assertEqual(deal.amount, lead.amount)


class LeadServiceTest(TestCase):
    """Test LeadService functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.lead_status = LeadStatus.objects.create(
            name='New',
            description='New lead status'
        )
    
    def test_create_lead(self):
        """Test lead creation through service."""
        data = {
            'title': 'Test Lead',
            'description': 'Test description',
            'amount': 5000,
            'currency': 'USD',
            'lead_status_id': self.lead_status.id
        }
        
        lead = LeadService.create_lead(self.user, data)
        
        self.assertEqual(lead.title, 'Test Lead')
        self.assertEqual(lead.user_created_id, self.user.id)
        self.assertEqual(lead.user_owner_id, self.user.id)
    
    def test_update_lead(self):
        """Test lead update through service."""
        lead = Lead.objects.create(
            title='Original Title',
            user_created_id=self.user.id,
            user_owner_id=self.user.id
        )
        
        data = {'title': 'Updated Title'}
        updated_lead = LeadService.update_lead(self.user, lead, data)
        
        self.assertEqual(updated_lead.title, 'Updated Title')
        self.assertEqual(updated_lead.user_updated_id, self.user.id)
    
    def test_convert_lead_to_deal(self):
        """Test lead conversion through service."""
        lead = Lead.objects.create(
            title='Test Lead',
            user_created_id=self.user.id,
            user_owner_id=self.user.id
        )
        
        deal = LeadService.convert_lead_to_deal(self.user, lead)
        
        self.assertIsNotNone(deal.id)
        self.assertEqual(deal.title, lead.title)
        lead.refresh_from_db()
        self.assertIsNotNone(lead.converted_at)


class LeadSelectorTest(TestCase):
    """Test LeadSelector functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.lead_status = LeadStatus.objects.create(
            name='New',
            description='New lead status'
        )
        self.lead_source = LeadSource.objects.create(
            name='Website',
            description='Lead from website'
        )
    
    def test_get_queryset(self):
        """Test base queryset filtering."""
        # Create active lead
        active_lead = Lead.objects.create(
            title='Active Lead',
            user_created_id=self.user.id,
            user_owner_id=self.user.id
        )
        
        # Create deleted lead
        deleted_lead = Lead.objects.create(
            title='Deleted Lead',
            user_created_id=self.user.id,
            user_owner_id=self.user.id
        )
        deleted_lead.soft_delete(self.user.id)
        
        # Create converted lead
        converted_lead = Lead.objects.create(
            title='Converted Lead',
            user_created_id=self.user.id,
            user_owner_id=self.user.id,
            converted_at=timezone.now()
        )
        
        queryset = LeadSelector.get_queryset(self.user, include_converted=False)
        
        self.assertIn(active_lead, queryset)
        self.assertNotIn(deleted_lead, queryset)
        self.assertNotIn(converted_lead, queryset)
        
        queryset_converted = LeadSelector.get_queryset(self.user, include_converted=True)
        self.assertIn(active_lead, queryset_converted)
        self.assertIn(converted_lead, queryset_converted)
        self.assertNotIn(deleted_lead, queryset_converted)
    
    def test_filter_queryset(self):
        """Test queryset filtering."""
        lead1 = Lead.objects.create(
            title='Qualified Lead',
            qualified=True,
            lead_status_id=self.lead_status.id,
            user_created_id=self.user.id,
            user_owner_id=self.user.id
        )
        
        lead2 = Lead.objects.create(
            title='Unqualified Lead',
            qualified=False,
            user_created_id=self.user.id,
            user_owner_id=self.user.id
        )
        
        queryset = Lead.objects.filter(is_deleted=False)
        
        # Filter by qualified
        filtered = LeadSelector.filter_queryset(
            queryset, {'qualified': 'true'}
        )
        self.assertIn(lead1, filtered)
        self.assertNotIn(lead2, filtered)
        
        # Filter by status
        filtered = LeadSelector.filter_queryset(
            queryset, {'status_id': self.lead_status.id}
        )
        self.assertIn(lead1, filtered)
        self.assertNotIn(lead2, filtered)
    
    def test_search_queryset(self):
        """Test queryset searching."""
        lead1 = Lead.objects.create(
            title='Test Lead One',
            user_created_id=self.user.id,
            user_owner_id=self.user.id
        )
        
        lead2 = Lead.objects.create(
            title='Another Lead',
            user_created_id=self.user.id,
            user_owner_id=self.user.id
        )
        
        queryset = Lead.objects.filter(is_deleted=False)
        
        # Search for 'Test'
        results = LeadSelector.search_queryset(queryset, 'Test')
        self.assertIn(lead1, results)
        self.assertNotIn(lead2, results)
        
        # Search for 'Another'
        results = LeadSelector.search_queryset(queryset, 'Another')
        self.assertIn(lead2, results)
        self.assertNotIn(lead1, results)
