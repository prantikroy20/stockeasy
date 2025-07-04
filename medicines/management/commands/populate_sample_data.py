from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from medicines.models import Category, Supplier, Medicine, StockTransaction
from accounts.models import UserProfile
from datetime import date, timedelta
from decimal import Decimal
import random

class Command(BaseCommand):
    help = 'Populate the database with sample data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Medicine.objects.all().delete()
            Category.objects.all().delete()
            Supplier.objects.all().delete()
            StockTransaction.objects.all().delete()
            UserProfile.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.stdout.write('Creating sample data...')
        
        # Create users
        self.create_users()
        
        # Create categories
        self.create_categories()
        
        # Create suppliers
        self.create_suppliers()
        
        # Create medicines
        self.create_medicines()
        
        # Create transactions
        self.create_transactions()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data')
        )

    def create_users(self):
        """Create sample users with different roles"""
        users_data = [
            {
                'username': 'pharmacist1',
                'email': 'pharmacist1@example.com',
                'first_name': 'John',
                'last_name': 'Smith',
                'role': 'pharmacist',
                'phone': '+1234567890'
            },
            {
                'username': 'staff1',
                'email': 'staff1@example.com',
                'first_name': 'Jane',
                'last_name': 'Doe',
                'role': 'staff',
                'phone': '+1234567891'
            },
            {
                'username': 'viewer1',
                'email': 'viewer1@example.com',
                'first_name': 'Bob',
                'last_name': 'Johnson',
                'role': 'viewer',
                'phone': '+1234567892'
            }
        ]
        
        for user_data in users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                }
            )
            if created:
                user.set_password('password123')
                user.save()
                
                UserProfile.objects.create(
                    user=user,
                    role=user_data['role'],
                    phone_number=user_data['phone']
                )
                
                self.stdout.write(f'Created user: {user.username}')

    def create_categories(self):
        """Create medicine categories"""
        categories_data = [
            {'name': 'Antibiotics', 'description': 'Medicines that fight bacterial infections'},
            {'name': 'Pain Relief', 'description': 'Analgesics and anti-inflammatory drugs'},
            {'name': 'Cardiovascular', 'description': 'Heart and blood pressure medications'},
            {'name': 'Diabetes', 'description': 'Diabetes management medications'},
            {'name': 'Respiratory', 'description': 'Asthma and respiratory condition treatments'},
            {'name': 'Vitamins & Supplements', 'description': 'Nutritional supplements and vitamins'},
            {'name': 'Digestive Health', 'description': 'Stomach and digestive system medications'},
            {'name': 'Mental Health', 'description': 'Antidepressants and anxiety medications'},
        ]
        
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={'description': cat_data['description']}
            )
            if created:
                self.stdout.write(f'Created category: {category.name}')

    def create_suppliers(self):
        """Create medicine suppliers"""
        suppliers_data = [
            {
                'name': 'PharmaCorp Ltd',
                'contact_person': 'Michael Brown',
                'email': 'contact@pharmacorp.com',
                'phone': '+1555123456',
                'address': '123 Medical Plaza, Healthcare City, HC 12345'
            },
            {
                'name': 'MediSupply Inc',
                'contact_person': 'Sarah Wilson',
                'email': 'orders@medisupply.com',
                'phone': '+1555234567',
                'address': '456 Pharma Street, Medicine Town, MT 67890'
            },
            {
                'name': 'Global Health Solutions',
                'contact_person': 'David Lee',
                'email': 'sales@globalhealthsol.com',
                'phone': '+1555345678',
                'address': '789 Wellness Avenue, Health District, HD 54321'
            },
            {
                'name': 'BioMed Distributors',
                'contact_person': 'Lisa Chen',
                'email': 'info@biomedist.com',
                'phone': '+1555456789',
                'address': '321 Science Park, Research City, RC 98765'
            },
        ]
        
        for sup_data in suppliers_data:
            supplier, created = Supplier.objects.get_or_create(
                name=sup_data['name'],
                defaults=sup_data
            )
            if created:
                self.stdout.write(f'Created supplier: {supplier.name}')

    def create_medicines(self):
        """Create sample medicines"""
        categories = list(Category.objects.all())
        suppliers = list(Supplier.objects.all())
        
        medicines_data = [
            # Antibiotics
            {'name': 'Amoxicillin', 'generic_name': 'Amoxicillin', 'strength': '500mg', 'form': 'capsule', 'category': 'Antibiotics'},
            {'name': 'Azithromycin', 'generic_name': 'Azithromycin', 'strength': '250mg', 'form': 'tablet', 'category': 'Antibiotics'},
            {'name': 'Ciprofloxacin', 'generic_name': 'Ciprofloxacin', 'strength': '500mg', 'form': 'tablet', 'category': 'Antibiotics'},
            
            # Pain Relief
            {'name': 'Ibuprofen', 'generic_name': 'Ibuprofen', 'strength': '400mg', 'form': 'tablet', 'category': 'Pain Relief'},
            {'name': 'Paracetamol', 'generic_name': 'Acetaminophen', 'strength': '500mg', 'form': 'tablet', 'category': 'Pain Relief'},
            {'name': 'Aspirin', 'generic_name': 'Acetylsalicylic Acid', 'strength': '325mg', 'form': 'tablet', 'category': 'Pain Relief'},
            
            # Cardiovascular
            {'name': 'Lisinopril', 'generic_name': 'Lisinopril', 'strength': '10mg', 'form': 'tablet', 'category': 'Cardiovascular'},
            {'name': 'Amlodipine', 'generic_name': 'Amlodipine', 'strength': '5mg', 'form': 'tablet', 'category': 'Cardiovascular'},
            {'name': 'Metoprolol', 'generic_name': 'Metoprolol', 'strength': '50mg', 'form': 'tablet', 'category': 'Cardiovascular'},
            
            # Diabetes
            {'name': 'Metformin', 'generic_name': 'Metformin', 'strength': '500mg', 'form': 'tablet', 'category': 'Diabetes'},
            {'name': 'Insulin Glargine', 'generic_name': 'Insulin Glargine', 'strength': '100 units/ml', 'form': 'injection', 'category': 'Diabetes'},
            
            # Respiratory
            {'name': 'Salbutamol Inhaler', 'generic_name': 'Salbutamol', 'strength': '100mcg', 'form': 'inhaler', 'category': 'Respiratory'},
            {'name': 'Montelukast', 'generic_name': 'Montelukast', 'strength': '10mg', 'form': 'tablet', 'category': 'Respiratory'},
            
            # Vitamins & Supplements
            {'name': 'Vitamin D3', 'generic_name': 'Cholecalciferol', 'strength': '1000 IU', 'form': 'tablet', 'category': 'Vitamins & Supplements'},
            {'name': 'Multivitamin', 'generic_name': 'Multivitamin', 'strength': 'Daily', 'form': 'tablet', 'category': 'Vitamins & Supplements'},
            
            # Digestive Health
            {'name': 'Omeprazole', 'generic_name': 'Omeprazole', 'strength': '20mg', 'form': 'capsule', 'category': 'Digestive Health'},
            {'name': 'Loperamide', 'generic_name': 'Loperamide', 'strength': '2mg', 'form': 'tablet', 'category': 'Digestive Health'},
        ]
        
        admin_user = User.objects.filter(is_superuser=True).first()
        
        for med_data in medicines_data:
            category = Category.objects.get(name=med_data['category'])
            supplier = random.choice(suppliers)
            
            # Generate random prices and stock
            unit_price = Decimal(str(round(random.uniform(5.0, 50.0), 2)))
            selling_price = unit_price * Decimal('1.3')  # 30% markup
            current_stock = random.randint(10, 500)
            
            medicine, created = Medicine.objects.get_or_create(
                name=med_data['name'],
                strength=med_data['strength'],
                defaults={
                    'generic_name': med_data['generic_name'],
                    'category': category,
                    'supplier': supplier,
                    'dosage_form': med_data['form'],
                    'prescription_type': random.choice(['prescription', 'otc']),
                    'current_stock': current_stock,
                    'minimum_stock': random.randint(5, 20),
                    'maximum_stock': random.randint(200, 1000),
                    'unit_price': unit_price,
                    'selling_price': selling_price,
                    'manufacture_date': date.today() - timedelta(days=random.randint(30, 365)),
                    'expiry_date': date.today() + timedelta(days=random.randint(365, 1095)),
                    'batch_number': f'BATCH{random.randint(1000, 9999)}',
                    'created_by': admin_user,
                }
            )
            if created:
                self.stdout.write(f'Created medicine: {medicine.name}')

    def create_transactions(self):
        """Create sample stock transactions"""
        medicines = list(Medicine.objects.all())
        admin_user = User.objects.filter(is_superuser=True).first()
        
        # Create some purchase transactions
        for _ in range(20):
            medicine = random.choice(medicines)
            quantity = random.randint(50, 200)
            
            StockTransaction.objects.create(
                medicine=medicine,
                transaction_type='purchase',
                quantity=quantity,
                unit_price=medicine.unit_price,
                reference_number=f'PO{random.randint(1000, 9999)}',
                notes='Initial stock purchase',
                created_by=admin_user
            )
        
        # Create some sale transactions
        for _ in range(50):
            medicine = random.choice(medicines)
            if medicine.current_stock > 0:
                quantity = random.randint(1, min(10, medicine.current_stock))
                
                StockTransaction.objects.create(
                    medicine=medicine,
                    transaction_type='sale',
                    quantity=quantity,
                    unit_price=medicine.selling_price,
                    reference_number=f'SALE{random.randint(1000, 9999)}',
                    notes='Customer purchase',
                    created_by=admin_user
                )
        
        self.stdout.write('Created sample transactions')