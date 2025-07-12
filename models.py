# -*- coding: utf-8 -*-
"""
نماذج قاعدة البيانات لمعرض الطعام العربي المتقدم
Advanced Models for Arab Expo For Food Database
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import json
from sqlalchemy import func, and_, or_

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """نموذج المستخدم الأساسي - Base User Model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)  # admin, exhibitor, visitor
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # علاقات - Relationships
    exhibitor_profile = db.relationship('Exhibitor', backref='user', uselist=False, cascade='all, delete-orphan')
    visitor_profile = db.relationship('Visitor', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """تشفير كلمة المرور - Hash password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """التحقق من كلمة المرور - Check password"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """التحقق من صلاحيات الإدارة - Check admin privileges"""
        return self.user_type == 'admin'
    
    def is_exhibitor(self):
        """التحقق من كونه عارض - Check if exhibitor"""
        return self.user_type == 'exhibitor'
    
    def is_visitor(self):
        """التحقق من كونه زائر - Check if visitor"""
        return self.user_type == 'visitor'
    
    def __repr__(self):
        return f'<User {self.email}>'

class Category(db.Model):
    """نموذج أقسام المعرض - Exhibition Categories Model"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False)  # الاسم بالعربية
    name_en = db.Column(db.String(100), nullable=False)  # الاسم بالإنجليزية
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # أيقونة القسم
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # علاقات - Relationships
    exhibitors = db.relationship('Exhibitor', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<Category {self.name_en}>'

class Exhibitor(db.Model):
    """نموذج العارض - Exhibitor Model"""
    __tablename__ = 'exhibitors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    
    # بيانات الشركة - Company Information
    company_name = db.Column(db.String(150), nullable=False)
    company_description = db.Column(db.Text)
    company_website = db.Column(db.String(255))
    company_address = db.Column(db.Text)
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    
    # الصور والملفات - Images and Files
    logo_image = db.Column(db.String(255))  # شعار الشركة
    cover_image = db.Column(db.String(255))  # صورة الغلاف
    brochure_file = db.Column(db.String(255))  # ملف البروشور
    
    # معلومات المعرض - Exhibition Information
    booth_size = db.Column(db.String(50))  # حجم الكشك
    booth_type = db.Column(db.String(50))  # نوع الكشك
    special_requirements = db.Column(db.Text)  # متطلبات خاصة
    
    # حالة التسجيل - Registration Status
    registration_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    payment_status = db.Column(db.String(20), default='unpaid')  # unpaid, paid, refunded
    
    # إحصائيات - Statistics
    profile_views = db.Column(db.Integer, default=0)
    total_products = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # علاقات - Relationships
    products = db.relationship('Product', backref='exhibitor', lazy=True, cascade='all, delete-orphan')
    exhibition_visits = db.relationship('ExhibitionVisit', backref='exhibitor', lazy=True)
    
    def get_total_products(self):
        """حساب إجمالي المنتجات - Calculate total products"""
        return len(self.products)
    
    def get_profile_completion_percentage(self):
        """حساب نسبة اكتمال الملف الشخصي - Calculate profile completion percentage"""
        fields = [
            self.company_name, self.company_description, self.logo_image,
            self.cover_image, self.country, self.city, self.booth_size
        ]
        completed = sum(1 for field in fields if field)
        return int((completed / len(fields)) * 100)
    
    def __repr__(self):
        return f'<Exhibitor {self.company_name}'

class Visitor(db.Model):
    """نموذج الزائر - Visitor Model"""
    __tablename__ = 'visitors'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # معلومات شخصية - Personal Information
    job_title = db.Column(db.String(100))
    company_name = db.Column(db.String(150))
    industry = db.Column(db.String(100))
    country = db.Column(db.String(100))
    city = db.Column(db.String(100))
    
    # اهتمامات - Interests
    interests = db.Column(db.Text)  # JSON format
    
    # إحصائيات - Statistics
    total_visits = db.Column(db.Integer, default=0)
    favorite_exhibitors = db.Column(db.Text)  # JSON format for exhibitor IDs
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # علاقات - Relationships
    exhibition_visits = db.relationship('ExhibitionVisit', backref='visitor', lazy=True)
    
    def __repr__(self):
        return f'<Visitor {self.company_name if self.company_name else "Individual"}>'
    
    def get_total_visits(self):
        """جلب عدد الزيارات الكلي - Get Total Visits Count"""
        return len(self.exhibition_visits)
    
    def get_visited_exhibitors_count(self):
        """جلب عدد العارضين المزارين - Get Visited Exhibitors Count"""
        visited_exhibitors = set()
        for visit in self.exhibition_visits:
            visited_exhibitors.add(visit.exhibitor_id)
        return len(visited_exhibitors)
    
    def get_favorite_products_count(self):
        """جلب عدد المنتجات المفضلة - Get Favorite Products Count"""
        if not self.favorite_exhibitors:
            return 0
        try:
            import json
            favorites = json.loads(self.favorite_exhibitors)
            return len(favorites) if isinstance(favorites, list) else 0
        except:
            return 0
    
    def add_to_favorites(self, exhibitor_id):
        """إضافة عارض للمفضلة - Add Exhibitor to Favorites"""
        try:
            import json
            if self.favorite_exhibitors:
                favorites = json.loads(self.favorite_exhibitors)
            else:
                favorites = []
            
            if exhibitor_id not in favorites:
                favorites.append(exhibitor_id)
                self.favorite_exhibitors = json.dumps(favorites)
                return True
            return False
        except:
            self.favorite_exhibitors = json.dumps([exhibitor_id])
            return True
    
    def remove_from_favorites(self, exhibitor_id):
        """إزالة عارض من المفضلة - Remove Exhibitor from Favorites"""
        try:
            import json
            if self.favorite_exhibitors:
                favorites = json.loads(self.favorite_exhibitors)
                if exhibitor_id in favorites:
                    favorites.remove(exhibitor_id)
                    self.favorite_exhibitors = json.dumps(favorites)
                    return True
            return False
        except:
            return False

class Product(db.Model):
    """نموذج المنتج - Product Model"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    exhibitor_id = db.Column(db.Integer, db.ForeignKey('exhibitors.id'), nullable=False)
    
    # معلومات المنتج - Product Information
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    currency = db.Column(db.String(10), default='USD')
    
    # الصور - Images
    main_image = db.Column(db.String(255))
    gallery_images = db.Column(db.Text)  # JSON format for multiple images
    
    # التصنيف - Classification
    category = db.Column(db.String(100))
    tags = db.Column(db.Text)  # JSON format
    
    # الحالة - Status
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    
    # إحصائيات - Statistics
    views_count = db.Column(db.Integer, default=0)
    inquiries_count = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Product {self.name}>'

class ExhibitionVisit(db.Model):
    """نموذج زيارات المعرض - Exhibition Visits Model"""
    __tablename__ = 'exhibition_visits'
    
    id = db.Column(db.Integer, primary_key=True)
    visitor_id = db.Column(db.Integer, db.ForeignKey('visitors.id'), nullable=False)
    exhibitor_id = db.Column(db.Integer, db.ForeignKey('exhibitors.id'), nullable=False)
    
    visit_date = db.Column(db.DateTime, default=datetime.utcnow)
    duration_minutes = db.Column(db.Integer, default=0)
    pages_viewed = db.Column(db.Integer, default=1)
    
    # تفاعلات - Interactions
    downloaded_brochure = db.Column(db.Boolean, default=False)
    contacted_exhibitor = db.Column(db.Boolean, default=False)
    added_to_favorites = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Visit {self.visitor_id} -> {self.exhibitor_id}>'

class SystemStats(db.Model):
    """نموذج إحصائيات النظام - System Statistics Model"""
    __tablename__ = 'system_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, default=datetime.utcnow().date, unique=True)
    
    # إحصائيات يومية - Daily Statistics
    new_users = db.Column(db.Integer, default=0)
    new_exhibitors = db.Column(db.Integer, default=0)
    new_visitors = db.Column(db.Integer, default=0)
    new_products = db.Column(db.Integer, default=0)
    
    # إحصائيات النشاط - Activity Statistics
    total_visits = db.Column(db.Integer, default=0)
    total_page_views = db.Column(db.Integer, default=0)
    brochure_downloads = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SystemStats {self.date}>'

class HomePageContent(db.Model):
    """نموذج محتوى الصفحة الرئيسية - Home Page Content Model"""
    __tablename__ = 'home_page_content'
    
    id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(50), nullable=False, unique=True)  # banner, video, pavilions, etc.
    
    # محتوى النص - Text Content
    title_ar = db.Column(db.String(255))  # العنوان بالعربية
    title_en = db.Column(db.String(255))  # العنوان بالإنجليزية
    subtitle_ar = db.Column(db.Text)      # العنوان الفرعي بالعربية
    subtitle_en = db.Column(db.Text)      # العنوان الفرعي بالإنجليزية
    description_ar = db.Column(db.Text)   # الوصف بالعربية
    description_en = db.Column(db.Text)   # الوصف بالإنجليزية
    
    # الصور والملفات - Images and Files
    main_image = db.Column(db.String(255))      # الصورة الرئيسية
    background_image = db.Column(db.String(255)) # صورة الخلفية
    gallery_images = db.Column(db.Text)         # صور إضافية (JSON)
    video_url = db.Column(db.String(500))       # رابط الفيديو
    video_file = db.Column(db.String(255))      # ملف الفيديو المرفوع
    download_file = db.Column(db.String(255))   # ملف التحميل
    pdf_file = db.Column(db.String(255))        # ملف PDF للقسم
    attachment_file = db.Column(db.String(255)) # ملف مرفق إضافي
    
    # إعدادات العرض - Display Settings
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    custom_css = db.Column(db.Text)             # CSS مخصص
    custom_data = db.Column(db.Text)            # بيانات إضافية (JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_gallery_images(self):
        """الحصول على قائمة الصور الإضافية - Get gallery images list"""
        if self.gallery_images:
            import json
            try:
                return json.loads(self.gallery_images)
            except:
                return []
        return []
    
    def set_gallery_images(self, images_list):
        """تعيين قائمة الصور الإضافية - Set gallery images list"""
        import json
        self.gallery_images = json.dumps(images_list)
    
    def get_custom_data(self):
        """الحصول على البيانات المخصصة - Get custom data"""
        if self.custom_data:
            import json
            try:
                return json.loads(self.custom_data)
            except:
                return {}
        return {}
    
    def set_custom_data(self, data_dict):
        """تعيين البيانات المخصصة - Set custom data"""
        import json
        self.custom_data = json.dumps(data_dict)
    
    @staticmethod
    def get_section(section_name):
        """الحصول على قسم معين - Get specific section"""
        return HomePageContent.query.filter_by(section_name=section_name).first()
    
    @staticmethod
    def get_active_sections():
        """الحصول على جميع الأقسام النشطة - Get all active sections"""
        return HomePageContent.query.filter_by(is_active=True)\
                                   .order_by(HomePageContent.display_order)\
                                   .all()
    
    def __repr__(self):
        return f'<HomePageContent {self.section_name}'

# دوال مساعدة - Helper Functions
def create_default_categories():
    """إنشاء الأقسام الافتراضية - Create default categories"""
    default_categories = [
        {'name_ar': 'منتجات الألبان', 'name_en': 'Dairy Products', 'icon': 'fas fa-cheese'},
        {'name_ar': 'المشروبات', 'name_en': 'Beverages', 'icon': 'fas fa-glass-water'},
        {'name_ar': 'اللحوم والدواجن', 'name_en': 'Meat & Poultry', 'icon': 'fas fa-drumstick-bite'},
        {'name_ar': 'الحبوب والبقوليات', 'name_en': 'Grains & Legumes', 'icon': 'fas fa-seedling'},
        {'name_ar': 'الفواكه والخضروات', 'name_en': 'Fruits & Vegetables', 'icon': 'fas fa-apple-alt'},
        {'name_ar': 'المخبوزات', 'name_en': 'Bakery Products', 'icon': 'fas fa-bread-slice'},
        {'name_ar': 'المعدات والآلات', 'name_en': 'Equipment & Machinery', 'icon': 'fas fa-cogs'},
        {'name_ar': 'التعبئة والتغليف', 'name_en': 'Packaging', 'icon': 'fas fa-box'},
    ]
    
    for cat_data in default_categories:
        if not Category.query.filter_by(name_en=cat_data['name_en']).first():
            category = Category(**cat_data)
            db.session.add(category)
    
    db.session.commit()

def create_admin_user():
    """إنشاء مستخدم إداري افتراضي - Create default admin user"""
    admin_email = 'admin@arabexpo.com'
    if not User.query.filter_by(email=admin_email).first():
        admin = User(
            email=admin_email,
            full_name='مدير النظام',
            phone='+966123456789',
            user_type='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print(f"تم إنشاء المستخدم الإداري: {admin_email} / admin123")

def create_default_home_content():
    """إنشاء محتوى افتراضي للصفحة الرئيسية - Create default home page content"""
    default_sections = [
        {
            'section_name': 'main_banner',
            'title_ar': 'معرض الطعام العربي',
            'title_en': 'Arab Expo For Food',
            'subtitle_ar': 'المعرض الافتراضي الدولي للأغذية والمشروبات وتكنولوجيا صناعة الطعام',
            'subtitle_en': 'The International Virtual Exhibition and Conference for Food, Beverage, and F&B Industry Technology.',
            'description_ar': 'مساحة افتراضية للأعمال الحقيقية • معرض الطعام العربي يجمع مجتمع الأغذية والمشروبات الدولي لاستكشاف فرص جديدة في أسواق أفريقيا والشرق الأوسط والخليج العربي والبحر الأبيض المتوسط.',
            'description_en': 'Virtual Space for Real Business • Arab expo for food brings together the international food & beverage community to explore new opportunities in the Africa, Middle East, Arabian Gulf and Mediterranean Sea markets.',
            'is_active': True,
            'display_order': 1
        },
        {
            'section_name': 'intro_video',
            'title_ar': 'معرض الطعام العربي',
            'title_en': 'Arab Expo For Food',
            'description_ar': 'شاهد الفيديو التعريفي للمعرض',
            'description_en': 'Watch the exhibition introduction video',
            'is_active': True,
            'display_order': 2
        },
        {
            'section_name': 'pavilions',
            'title_ar': 'أجنحة المعرض',
            'title_en': 'Exhibition Pavilions',
            'description_ar': 'استكشف الأجنحة المتخصصة للمعرض',
            'description_en': 'Explore the specialized exhibition pavilions',
            'is_active': True,
            'display_order': 3
        },
        {
            'section_name': 'sponsors',
            'title_ar': 'رعاتنا',
            'title_en': 'Our Sponsors',
            'description_ar': 'شركاؤنا الداعمون للمعرض',
            'description_en': 'Our supporting partners for the exhibition',
            'is_active': True,
            'display_order': 4
        },
        {
            'section_name': 'featured_products',
            'title_ar': 'المنتجات المميزة',
            'title_en': 'Recommended Products',
            'description_ar': 'تعرف على أحدث المنتجات المميزة',
            'description_en': 'Discover the latest featured products',
            'is_active': True,
            'display_order': 5
        },
        {
            'section_name': 'target_countries',
            'title_ar': 'الدول والمدن المستهدفة',
            'title_en': 'Targeted Countries & Cities',
            'description_ar': 'الأسواق التي نستهدفها في المعرض',
            'description_en': 'The markets we target in the exhibition',
            'is_active': True,
            'display_order': 6
        },
        {
            'section_name': 'pavilion_types',
            'title_ar': 'أشكال الأكشاك المتنوعة',
            'title_en': 'Various Booth Shapes',
            'description_ar': 'معرض الطعام العربي يوفر أشكال متنوعة لكشكك\nخصص متجرك',
            'description_en': 'Arab Expo offers many shapes for your booth\n Customize your store',
            'is_active': True,
            'display_order': 7
        },
        {
            'section_name': 'events',
            'title_ar': 'فعاليات معرض الطعام العربي',
            'title_en': 'Arab Expo Events',
            'description_ar': 'اكتشف فعاليات ومؤتمرات المعرض',
            'description_en': 'Discover exhibition events and conferences',
            'is_active': True,
            'display_order': 8
        }
    ]
    
    for section_data in default_sections:
        existing = HomePageContent.query.filter_by(section_name=section_data['section_name']).first()
        if not existing:
            section = HomePageContent(**section_data)
            db.session.add(section)
    
    db.session.commit()

def init_db(app):
    """تهيئة قاعدة البيانات - Initialize database"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        create_default_categories()
        create_admin_user()
        create_default_home_content()
        print("تم تهيئة قاعدة البيانات بنجاح!")
