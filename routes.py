# -*- coding: utf-8 -*-
"""
روتات تطبيق معرض الطعام العربي
Routes for Arab Expo For Food Application
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os
import json
from sqlalchemy import func, and_, or_
from models import db, User, Exhibitor, Visitor, Product, Category, ExhibitionVisit, SystemStats, HomePageContent
from device_detector import DeviceDetector

# دالة مساعدة لاختيار القالب المناسب - Helper function to choose appropriate template
def render_device_template(template_name, **context):
    """اختيار القالب المناسب حسب نوع الجهاز - Choose appropriate template based on device type"""
    device_type = DeviceDetector.get_device_type()
    
    if device_type == 'mobile':
        # للموبايل: استخدم صفحات mobile/ إذا وُجدت
        mobile_template = f'mobile/{template_name}'
        try:
            return render_template(mobile_template, **context)
        except:
            # إذا لم توجد صفحة موبايل، استخدم الصفحة العادية
            return render_template(template_name, **context)
    else:
        # للديسكتوب والتابلت: استخدم الصفحات العادية
        return render_template(template_name, **context)

# إنشاء البلو برينت الرئيسي - Main Blueprint
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
exhibitor_bp = Blueprint('exhibitor', __name__, url_prefix='/exhibitor')
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
api_bp = Blueprint('api', __name__, url_prefix='/api')

# إعدادات رفع الملفات - File Upload Settings
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv'}
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB for videos

def allowed_file(filename):
    """التحقق من صيغة الملف المسموحة - Check allowed file format"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, upload_folder):
    """حفظ الملف المرفوع - Save uploaded file"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # إضافة timestamp لتجنب تضارب الأسماء
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        filepath = os.path.join(upload_folder, filename)
        
        try:
            # إنشاء المجلد إذا لم يكن موجوداً
            os.makedirs(upload_folder, exist_ok=True)
            
            # حفظ الملف مع دعم للملفات الكبيرة
            file.save(filepath)
            return filename
        except Exception as e:
            current_app.logger.error(f"Error saving file {filename}: {str(e)}")
            return None
    return None

# ==================== الروتات الرئيسية - Main Routes ====================

@main_bp.route('/')
def index():
    """الصفحة الرئيسية - Home Page"""
    # إحصائيات سريعة للصفحة الرئيسية
    stats = {
        'total_exhibitors': Exhibitor.query.filter_by(registration_status='approved').count(),
        'total_visitors': Visitor.query.count(),
        'total_products': Product.query.filter_by(is_active=True).count(),
        'total_categories': Category.query.filter_by(is_active=True).count()
    }
    
    # أحدث العارضين المعتمدين
    latest_exhibitors = Exhibitor.query.filter_by(registration_status='approved')\
                                      .order_by(Exhibitor.created_at.desc())\
                                      .limit(6).all()
    
    # المنتجات المميزة - جلب العدد من إعدادات الأدمن أو استخدام القيمة الافتراضية
    featured_products_settings = HomePageContent.get_section('featured_products')
    products_count = 8  # القيمة الافتراضية
    
    if featured_products_settings and featured_products_settings.is_active:
        custom_data = featured_products_settings.get_custom_data()
        products_count = custom_data.get('products_count', 8)
        selection_criteria = custom_data.get('selection_criteria', 'views')
        
        # اختيار المنتجات حسب المعايير المحددة
        if selection_criteria == 'recent':
            featured_products = Product.query.filter_by(is_active=True)\
                                           .join(Exhibitor)\
                                           .filter(Exhibitor.registration_status == 'approved')\
                                           .order_by(Product.created_at.desc())\
                                           .limit(products_count).all()
        elif selection_criteria == 'views':
            featured_products = Product.query.filter_by(is_active=True)\
                                           .join(Exhibitor)\
                                           .filter(Exhibitor.registration_status == 'approved')\
                                           .order_by(Product.views_count.desc())\
                                           .limit(products_count).all()
        else:  # manual or featured
            featured_products = Product.query.filter_by(is_featured=True, is_active=True)\
                                           .join(Exhibitor)\
                                           .filter(Exhibitor.registration_status == 'approved')\
                                           .order_by(Product.created_at.desc())\
                                           .limit(products_count).all()
    else:
        # إعدادات افتراضية إذا لم يتم تكوين القسم
        featured_products = Product.query.filter_by(is_featured=True, is_active=True)\
                                       .join(Exhibitor)\
                                       .filter(Exhibitor.registration_status == 'approved')\
                                       .order_by(Product.created_at.desc())\
                                       .limit(products_count).all()
    
    # جلب محتوى جميع أقسام الصفحة الرئيسية النشطة
    home_sections = HomePageContent.get_active_sections()
    
    # تنظيم الأقسام في قاموس لسهولة الوصول
    sections_data = {}
    for section in home_sections:
        sections_data[section.section_name] = section
    
    return render_device_template('index.html', 
                         stats=stats, 
                         latest_exhibitors=latest_exhibitors,
                         featured_products=featured_products,
                         home_sections=sections_data)

@main_bp.route('/pavilions-flags')
def pavilions_flags():
    """صفحة أعلام الدول العربية - Arab Countries Flags Page"""
    return render_device_template('pavilions_flags.html')

@main_bp.route('/exhibitors-by-country/<country>')
def exhibitors_by_country(country):
    """عرض العارضين حسب الدولة - Display Exhibitors by Country"""
    page = request.args.get('page', 1, type=int)
    per_page = 12  # عدد العارضين في كل صفحة
    
    # خريطة أسماء الدول
    country_names = {
        'EG': 'مصر',
        'SA': 'السعودية', 
        'AE': 'الإمارات',
        'KW': 'الكويت',
        'QA': 'قطر',
        'BH': 'البحرين',
        'OM': 'عمان',
        'IQ': 'العراق',
        'JO': 'الأردن',
        'LB': 'لبنان',
        'SY': 'سوريا',
        'PS': 'فلسطين',
        'MA': 'المغرب',
        'DZ': 'الجزائر',
        'TN': 'تونس',
        'LY': 'ليبيا',
        'SD': 'السودان',
        'SO': 'الصومال',
        'DJ': 'جيبوتي',
        'MR': 'موريتانيا',
        'YE': 'اليمن',
        'KM': 'جزر القمر'
    }
    
    country_display_name = country_names.get(country, country)
    
    # البحث عن العارضين من الدولة المحددة
    exhibitors = Exhibitor.query.filter(
        and_(
            Exhibitor.registration_status == 'approved',
            Exhibitor.country == country
        )
    ).order_by(Exhibitor.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # إحصائيات سريعة للدولة
    country_stats = {
        'total_exhibitors': exhibitors.total,
        'total_products': db.session.query(func.count(Product.id))\
                         .join(Exhibitor)\
                         .filter(and_(
                             Exhibitor.registration_status == 'approved',
                             Exhibitor.country == country,
                             Product.is_active == True
                         )).scalar() or 0
    }
    
    # الحصول على الأقسام المتاحة للدولة
    categories = db.session.query(Category, func.count(Exhibitor.id).label('count'))\
                          .join(Exhibitor, Category.id == Exhibitor.category_id, isouter=True)\
                          .filter(and_(
                              Exhibitor.registration_status == 'approved',
                              Exhibitor.country == country,
                              Category.is_active == True
                          ))\
                          .group_by(Category.id)\
                          .having(func.count(Exhibitor.id) > 0)\
                          .all()
    
    return render_device_template('exhibitors_by_country.html', 
                         exhibitors=exhibitors,
                         country=country_display_name,
                         country_stats=country_stats,
                         categories=categories)
    
    return render_device_template('exhibitors_by_country.html', 
                         exhibitors=exhibitors,
                         country=country,
                         country_stats=country_stats,
                         categories=categories)

@main_bp.route('/exhibitors')
def exhibitors_list():
    """قائمة العارضين - Exhibitors List"""
    page = request.args.get('page', 1, type=int)
    category_id = request.args.get('category', type=int)
    search = request.args.get('search', '')
    
    # بناء الاستعلام
    query = Exhibitor.query.filter_by(registration_status='approved')
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    if search:
        query = query.filter(or_(
            Exhibitor.company_name.contains(search),
            Exhibitor.company_description.contains(search)
        ))
    
    # ترقيم الصفحات
    exhibitors = query.order_by(Exhibitor.created_at.desc())\
                     .paginate(page=page, per_page=12, error_out=False)
    
    categories = Category.query.filter_by(is_active=True).all()
    
    return render_device_template('exhibitors_list.html', 
                         exhibitors=exhibitors, 
                         categories=categories,
                         current_category=category_id,
                         search_term=search)

@main_bp.route('/products')
def products_list():
    """قائمة المنتجات - Products List"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    exhibitor_id = request.args.get('exhibitor', type=int)
    search = request.args.get('search', '')
    sort_by = request.args.get('sort', 'newest')  # newest, oldest, name, price_low, price_high
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # بناء الاستعلام
    query = Product.query.filter_by(is_active=True)\
                   .join(Exhibitor)\
                   .filter(Exhibitor.registration_status == 'approved')
    
    # تصفية حسب الفئة
    if category:
        query = query.filter(Product.category == category)
    
    # تصفية حسب العارض
    if exhibitor_id:
        query = query.filter(Product.exhibitor_id == exhibitor_id)
    
    # تصفية حسب السعر
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # البحث النصي
    if search:
        query = query.filter(or_(
            Product.name.contains(search),
            Product.description.contains(search),
            Product.category.contains(search)
        ))
    
    # ترتيب النتائج
    if sort_by == 'oldest':
        query = query.order_by(Product.created_at.asc())
    elif sort_by == 'name':
        query = query.order_by(Product.name.asc())
    elif sort_by == 'price_low':
        query = query.order_by(Product.price.asc().nullslast())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc().nullsfirst())
    elif sort_by == 'featured':
        query = query.order_by(Product.is_featured.desc(), Product.created_at.desc())
    else:  # newest (default)
        query = query.order_by(Product.created_at.desc())
    
    # ترقيم الصفحات
    products = query.paginate(page=page, per_page=16, error_out=False)
    
    # جلب الفئات المتاحة
    available_categories = db.session.query(Product.category)\
                                   .filter(Product.is_active == True)\
                                   .filter(Product.category.isnot(None))\
                                   .distinct().all()
    categories = [cat[0] for cat in available_categories if cat[0]]
    
    # جلب العارضين المتاحين
    exhibitors = Exhibitor.query.filter_by(registration_status='approved')\
                               .filter(Exhibitor.id.in_(
                                   db.session.query(Product.exhibitor_id)\
                                           .filter_by(is_active=True)\
                                           .distinct()
                               ))\
                               .order_by(Exhibitor.company_name.asc()).all()
    
    # إحصائيات سريعة
    stats = {
        'total_products': Product.query.filter_by(is_active=True).count(),
        'total_exhibitors': len(exhibitors),
        'total_categories': len(categories)
    }
    
    return render_device_template('products_list.html', 
                         products=products,
                         categories=categories,
                         exhibitors=exhibitors,
                         stats=stats,
                         current_category=category,
                         current_exhibitor=exhibitor_id,
                         search_term=search,
                         sort_by=sort_by,
                         min_price=min_price,
                         max_price=max_price)

@main_bp.route('/exhibitor/<int:exhibitor_id>')
def exhibitor_profile(exhibitor_id):
    """صفحة العارض - Exhibitor Profile"""
    exhibitor = Exhibitor.query.get_or_404(exhibitor_id)
    
    # التحقق من أن العارض معتمد
    if exhibitor.registration_status != 'approved':
        flash('هذا العارض غير متاح حالياً', 'error')
        return redirect(url_for('main.exhibitors_list'))
    
    # زيادة عدد المشاهدات
    exhibitor.profile_views += 1
    
    # تسجيل الزيارة إذا كان المستخدم زائر مسجل
    if current_user.is_authenticated and current_user.is_visitor():
        visitor = current_user.visitor_profile
        if visitor:
            # البحث عن زيارة سابقة اليوم
            today = datetime.now().date()
            existing_visit = ExhibitionVisit.query.filter(
                and_(
                    ExhibitionVisit.visitor_id == visitor.id,
                    ExhibitionVisit.exhibitor_id == exhibitor.id,
                    func.date(ExhibitionVisit.visit_date) == today
                )
            ).first()
            
            if not existing_visit:
                visit = ExhibitionVisit(
                    visitor_id=visitor.id,
                    exhibitor_id=exhibitor.id
                )
                db.session.add(visit)
                visitor.total_visits += 1
    
    # منتجات العارض
    products = Product.query.filter_by(exhibitor_id=exhibitor.id, is_active=True)\
                          .order_by(Product.is_featured.desc(), Product.created_at.desc())\
                          .all()
    
    # جلب الفئات الموجودة في منتجات العارض
    product_categories = list(set([p.category for p in products if p.category]))
    
    db.session.commit()
    
    # اختيار القالب المناسب حسب نوع الجهاز
    device_type = DeviceDetector.get_device_type()
    template = 'mobile/exhibitor_profile.html' if device_type == 'mobile' else 'exhibitor_profile.html'
    
    return render_template(template, 
                         exhibitor=exhibitor, 
                         products=products,
                         product_categories=product_categories)

@main_bp.route('/exhibitor/<int:exhibitor_id>/record-visit', methods=['POST'])
@login_required
def record_visit(exhibitor_id):
    """تسجيل زيارة للعارض - Record Visit to Exhibitor"""
    if not current_user.is_visitor():
        return jsonify({'success': False, 'message': 'يجب أن تكون زائراً لتسجيل الزيارة'})
    
    exhibitor = Exhibitor.query.get_or_404(exhibitor_id)
    visitor = current_user.visitor_profile
    
    # التحقق من وجود زيارة سابقة اليوم
    today = datetime.now().date()
    existing_visit = ExhibitionVisit.query.filter(
        ExhibitionVisit.exhibitor_id == exhibitor_id,
        ExhibitionVisit.visitor_id == visitor.id,
        func.date(ExhibitionVisit.visit_date) == today
    ).first()
    
    if existing_visit:
        return jsonify({'success': False, 'message': 'لقد سجلت زيارة لهذا العارض اليوم بالفعل'})
    
    # إنشاء زيارة جديدة
    visit = ExhibitionVisit(
        exhibitor_id=exhibitor_id,
        visitor_id=visitor.id,
        visit_date=datetime.now()
    )
    
    db.session.add(visit)
    visitor.total_visits += 1
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'تم تسجيل زيارتك بنجاح'})

@main_bp.route('/exhibitor/<int:exhibitor_id>/update-views', methods=['POST'])
def update_profile_views(exhibitor_id):
    """تحديث عدد مشاهدات العارض - Update Profile Views"""
    exhibitor = Exhibitor.query.get_or_404(exhibitor_id)
    exhibitor.profile_views += 1
    db.session.commit()
    return jsonify({'success': True})

@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """تفاصيل المنتج - Product Detail"""
    product = Product.query.get_or_404(product_id)
    
    # التحقق من أن المنتج نشط والعارض معتمد
    if not product.is_active or product.exhibitor.registration_status != 'approved':
        flash('هذا المنتج غير متاح حالياً', 'error')
        return redirect(url_for('main.exhibitors_list'))
    
    # زيادة عدد المشاهدات
    product.views_count += 1
    db.session.commit()
    
    # منتجات مشابهة
    similar_products = Product.query.filter(
        and_(
            Product.exhibitor_id == product.exhibitor_id,
            Product.id != product.id,
            Product.is_active == True
        )
    ).limit(4).all()
    
    return render_device_template('product_detail.html', 
                         product=product, 
                         similar_products=similar_products)

# ==================== روتات المصادقة - Authentication Routes ====================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """تسجيل الدخول - Login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password) and user.is_active:
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            login_user(user, remember=remember)
            
            # توجيه المستخدم حسب نوعه
            next_page = request.args.get('next')
            if not next_page:
                if user.is_admin():
                    next_page = url_for('admin.dashboard')
                elif user.is_exhibitor():
                    next_page = url_for('exhibitor.dashboard')
                else:
                    next_page = url_for('main.index')
            
            flash('تم تسجيل الدخول بنجاح!', 'success')
            return redirect(next_page)
        else:
            flash('بريد إلكتروني أو كلمة مرور خاطئة', 'error')
    
    return render_device_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """التسجيل - Registration"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        user_type = request.form.get('user_type')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        
        # التحقق من وجود المستخدم
        if User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني مستخدم بالفعل', 'error')
            return render_device_template('auth/register.html')
        
        # إنشاء المستخدم الجديد
        user = User(
            email=email,
            full_name=full_name,
            phone=phone,
            user_type=user_type
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()  # للحصول على user.id
        
        # إنشاء الملف الشخصي حسب نوع المستخدم
        if user_type == 'exhibitor':
            company_name = request.form.get('company_name')
            exhibitor = Exhibitor(
                user_id=user.id,
                company_name=company_name
            )
            db.session.add(exhibitor)
        elif user_type == 'visitor':
            visitor = Visitor(user_id=user.id)
            db.session.add(visitor)
        
        db.session.commit()
        
        flash('تم إنشاء الحساب بنجاح! يمكنك الآن تسجيل الدخول', 'success')
        return redirect(url_for('auth.login'))
    
    categories = Category.query.filter_by(is_active=True).all()
    return render_device_template('auth/register.html', categories=categories)

@auth_bp.route('/logout')
@login_required
def logout():
    """تسجيل الخروج - Logout"""
    logout_user()
    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('main.index'))

# ==================== روتات العارض - Exhibitor Routes ====================

@exhibitor_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة تحكم العارض - Exhibitor Dashboard"""
    if not current_user.is_exhibitor():
        flash('غير مصرح لك بالوصول لهذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    exhibitor = current_user.exhibitor_profile
    if not exhibitor:
        flash('لم يتم العثور على ملف العارض', 'error')
        return redirect(url_for('main.index'))
    
    # إحصائيات العارض
    stats = {
        'total_products': exhibitor.get_total_products(),
        'profile_views': exhibitor.profile_views,
        'total_visits': ExhibitionVisit.query.filter_by(exhibitor_id=exhibitor.id).count(),
        'completion_percentage': exhibitor.get_profile_completion_percentage()
    }
    
    # المنتجات الأخيرة
    recent_products = Product.query.filter_by(exhibitor_id=exhibitor.id)\
                                 .order_by(Product.created_at.desc())\
                                 .limit(5).all()
    
    # الزيارات الأخيرة
    recent_visits = ExhibitionVisit.query.filter_by(exhibitor_id=exhibitor.id)\
                                        .order_by(ExhibitionVisit.visit_date.desc())\
                                        .limit(10).all()
    
    return render_device_template('exhibitor/dashboard.html', 
                         exhibitor=exhibitor, 
                         stats=stats,
                         recent_products=recent_products,
                         recent_visits=recent_visits)

@exhibitor_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """تحرير ملف العارض - Edit Exhibitor Profile"""
    if not current_user.is_exhibitor():
        flash('غير مصرح لك بالوصول لهذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    exhibitor = current_user.exhibitor_profile
    
    if request.method == 'POST':
        # تحديث البيانات الأساسية
        exhibitor.company_name = request.form.get('company_name')
        exhibitor.company_description = request.form.get('company_description')
        exhibitor.company_website = request.form.get('company_website')
        exhibitor.company_address = request.form.get('company_address')
        exhibitor.country = request.form.get('country')
        exhibitor.city = request.form.get('city')
        exhibitor.category_id = request.form.get('category_id') or None
        exhibitor.booth_size = request.form.get('booth_size')
        exhibitor.booth_type = request.form.get('booth_type')
        exhibitor.special_requirements = request.form.get('special_requirements')
        
        # رفع الصور
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'exhibitors')
        os.makedirs(upload_folder, exist_ok=True)
        
        if 'logo_image' in request.files:
            logo_file = request.files['logo_image']
            if logo_file.filename:
                logo_filename = save_uploaded_file(logo_file, upload_folder)
                if logo_filename:
                    exhibitor.logo_image = logo_filename
        
        if 'cover_image' in request.files:
            cover_file = request.files['cover_image']
            if cover_file.filename:
                cover_filename = save_uploaded_file(cover_file, upload_folder)
                if cover_filename:
                    exhibitor.cover_image = cover_filename
        
        if 'brochure_file' in request.files:
            brochure_file = request.files['brochure_file']
            if brochure_file.filename:
                brochure_filename = save_uploaded_file(brochure_file, upload_folder)
                if brochure_filename:
                    exhibitor.brochure_file = brochure_filename
        
        exhibitor.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('تم تحديث الملف الشخصي بنجاح!', 'success')
        return redirect(url_for('exhibitor.profile'))
    
    categories = Category.query.filter_by(is_active=True).all()
    
    # اختيار القالب المناسب حسب نوع الجهاز
    device_type = DeviceDetector.get_device_type()
    template = 'mobile/exhibitor/profile.html' if device_type == 'mobile' else 'exhibitor/profile.html'
    
    return render_template(template, 
                         exhibitor=exhibitor, 
                         categories=categories)

@exhibitor_bp.route('/products')
@login_required
def products():
    """منتجات العارض - Exhibitor Products"""
    if not current_user.is_exhibitor():
        flash('غير مصرح لك بالوصول لهذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    exhibitor = current_user.exhibitor_profile
    page = request.args.get('page', 1, type=int)
    
    products = Product.query.filter_by(exhibitor_id=exhibitor.id)\
                          .order_by(Product.created_at.desc())\
                          .paginate(page=page, per_page=10, error_out=False)
    
    return render_device_template('exhibitor/products.html', 
                         products=products, 
                         exhibitor=exhibitor)

@exhibitor_bp.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """إضافة منتج جديد - Add New Product"""
    if not current_user.is_exhibitor():
        flash('غير مصرح لك بالوصول لهذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    exhibitor = current_user.exhibitor_profile
    
    if request.method == 'POST':
        product = Product(
            exhibitor_id=exhibitor.id,
            name=request.form.get('name'),
            description=request.form.get('description'),
            price=float(request.form.get('price')) if request.form.get('price') else None,
            currency=request.form.get('currency', 'USD'),
            category=request.form.get('category'),
            is_featured=bool(request.form.get('is_featured'))
        )
        
        # رفع الصور
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products')
        os.makedirs(upload_folder, exist_ok=True)
        
        if 'main_image' in request.files:
            main_image_file = request.files['main_image']
            if main_image_file.filename:
                main_image_filename = save_uploaded_file(main_image_file, upload_folder)
                if main_image_filename:
                    product.main_image = main_image_filename
        
        # معالجة العلامات (Tags)
        tags = request.form.get('tags', '')
        if tags:
            tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            product.tags = json.dumps(tags_list)
        
        db.session.add(product)
        exhibitor.total_products = exhibitor.get_total_products() + 1
        db.session.commit()
        
        flash('تم إضافة المنتج بنجاح!', 'success')
        return redirect(url_for('exhibitor.products'))
    
    return render_device_template('exhibitor/add_product.html')

@exhibitor_bp.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    """تحرير منتج - Edit Product"""
    if not current_user.is_exhibitor():
        flash('غير مصرح لك بالوصول لهذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    exhibitor = current_user.exhibitor_profile
    product = Product.query.filter_by(id=product_id, exhibitor_id=exhibitor.id).first_or_404()
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price')) if request.form.get('price') else None
        product.currency = request.form.get('currency', 'USD')
        product.category = request.form.get('category')
        product.is_featured = bool(request.form.get('is_featured'))
        product.is_active = bool(request.form.get('is_active'))
        
        # رفع صورة جديدة إذا تم اختيارها
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products')
        if 'main_image' in request.files:
            main_image_file = request.files['main_image']
            if main_image_file.filename:
                main_image_filename = save_uploaded_file(main_image_file, upload_folder)
                if main_image_filename:
                    product.main_image = main_image_filename
        
        # معالجة العلامات
        tags = request.form.get('tags', '')
        if tags:
            tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            product.tags = json.dumps(tags_list)
        else:
            product.tags = None
        
        product.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('تم تحديث المنتج بنجاح!', 'success')
        return redirect(url_for('exhibitor.products'))
    
    # استخراج العلامات للعرض
    tags_display = ''
    if product.tags:
        try:
            tags_list = json.loads(product.tags)
            tags_display = ', '.join(tags_list)
        except:
            pass
    
    return render_device_template('exhibitor/edit_product.html', 
                         product=product, 
                         tags_display=tags_display)

@exhibitor_bp.route('/products/delete/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    """حذف منتج - Delete Product"""
    if not current_user.is_exhibitor():
        return jsonify({'success': False, 'message': 'غير مصرح لك بهذا الإجراء'})
    
    exhibitor = current_user.exhibitor_profile
    product = Product.query.filter_by(id=product_id, exhibitor_id=exhibitor.id).first()
    
    if not product:
        return jsonify({'success': False, 'message': 'المنتج غير موجود'})
    
    try:
        # حذف ملف الصورة إذا كان موجوداً
        if product.main_image:
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products', product.main_image)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(product)
        exhibitor.total_products = exhibitor.get_total_products() - 1
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'تم حذف المنتج بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء حذف المنتج'})

@exhibitor_bp.route('/products/toggle/<int:product_id>', methods=['POST'])
@login_required
def toggle_product_status(product_id):
    """تغيير حالة المنتج (تفعيل/إيقاف) - Toggle Product Status"""
    if not current_user.is_exhibitor():
        return jsonify({'success': False, 'message': 'غير مصرح لك بهذا الإجراء'})
    
    exhibitor = current_user.exhibitor_profile
    product = Product.query.filter_by(id=product_id, exhibitor_id=exhibitor.id).first()
    
    if not product:
        return jsonify({'success': False, 'message': 'المنتج غير موجود'})
    
    try:
        product.is_active = not product.is_active
        product.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = 'تم تفعيل' if product.is_active else 'تم إيقاف'
        return jsonify({'success': True, 'message': f'{status} المنتج بنجاح'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء تغيير حالة المنتج'})

# ==================== روتات الإدارة - Admin Routes ====================

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة تحكم الإدارة - Admin Dashboard"""
    if not current_user.is_admin():
        flash('غير مصرح لك بالوصول لهذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # إحصائيات عامة
    stats = {
        'total_users': User.query.count(),
        'total_exhibitors': Exhibitor.query.filter_by(registration_status='approved').count(),
        'total_visitors': Visitor.query.count(),
        'total_products': Product.query.filter_by(is_active=True).count(),
        'total_visits': ExhibitionVisit.query.count(),
        'pending_exhibitors': Exhibitor.query.filter_by(registration_status='pending').count(),
        'approved_exhibitors': Exhibitor.query.filter_by(registration_status='approved').count(),
        'rejected_exhibitors': Exhibitor.query.filter_by(registration_status='rejected').count(),
        'active_products': Product.query.filter_by(is_active=True).count(),
        'featured_products': Product.query.filter_by(is_featured=True, is_active=True).count(),
    }
    
    # إحصائيات الشهر الحالي
    current_month = datetime.now().replace(day=1)
    monthly_stats = {
        'new_users': User.query.filter(User.created_at >= current_month).count(),
        'new_exhibitors': Exhibitor.query.filter(Exhibitor.created_at >= current_month).count(),
        'new_visitors': Visitor.query.filter(Visitor.created_at >= current_month).count(),
        'new_products': Product.query.filter(Product.created_at >= current_month).count(),
    }
    
    # العارضين الجدد في انتظار الموافقة
    pending_exhibitors = Exhibitor.query.filter_by(registration_status='pending')\
                                       .order_by(Exhibitor.created_at.desc())\
                                       .limit(5).all()
    
    # أحدث المستخدمين
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # أحدث الأنشطة (يمكن توسيعها لاحقاً)
    recent_activities = []
    
    # اختيار القالب المناسب حسب نوع الجهاز
    device_type = DeviceDetector.get_device_type()
    
    if device_type == 'mobile':
        template_name = 'mobile/admin/dashboard.html'
    else:
        template_name = 'admin/dashboard.html'
    
    return render_template(template_name,
                         stats=stats,
                         monthly_stats=monthly_stats,
                         pending_exhibitors=pending_exhibitors,
                         recent_users=recent_users,
                         recent_activities=recent_activities,
                         current_date=datetime.now())

@admin_bp.route('/exhibitors')
@login_required
def exhibitors():
    """إدارة العارضين - Manage Exhibitors"""
    if not current_user.is_admin():
        flash('غير مصرح لك بالوصول لهذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', 'all')
    search = request.args.get('search', '')
    
    query = Exhibitor.query
    
    if status != 'all':
        query = query.filter_by(registration_status=status)
    
    if search:
        query = query.filter(or_(
            Exhibitor.company_name.contains(search),
            User.email.contains(search),
            User.full_name.contains(search)
        )).join(User)
    
    exhibitors = query.order_by(Exhibitor.created_at.desc())\
                     .paginate(page=page, per_page=20, error_out=False)
    
    # اختيار القالب المناسب حسب نوع الجهاز
    device_type = DeviceDetector.get_device_type()
    template = 'mobile/admin/exhibitors.html' if device_type == 'mobile' else 'admin/exhibitors.html'
    
    return render_template(template, 
                         exhibitors=exhibitors,
                         current_status=status,
                         search_term=search)

@admin_bp.route('/exhibitors/<int:exhibitor_id>/approve', methods=['POST'])
@login_required
def approve_exhibitor(exhibitor_id):
    """الموافقة على العارض - Approve Exhibitor"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'غير مصرح'}), 403
    
    exhibitor = Exhibitor.query.get_or_404(exhibitor_id)
    exhibitor.registration_status = 'approved'
    db.session.commit()
    
    flash(f'تم الموافقة على العارض {exhibitor.company_name}', 'success')
    return jsonify({'success': True})

@admin_bp.route('/exhibitors/<int:exhibitor_id>/reject', methods=['POST'])
@login_required
def reject_exhibitor(exhibitor_id):
    """رفض العارض - Reject Exhibitor"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'غير مصرح'}), 403
    
    exhibitor = Exhibitor.query.get_or_404(exhibitor_id)
    exhibitor.registration_status = 'rejected'
    db.session.commit()
    
    flash(f'تم رفض العارض {exhibitor.company_name}', 'warning')
    return jsonify({'success': True})

@admin_bp.route('/visitors')
@login_required
def visitors():
    """إدارة الزوار - Manage Visitors"""
    if not current_user.is_admin():
        flash('غير مصرح لك بالوصول لهذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    page = request.args.get('page', 1, type=int)
    visitor_type = request.args.get('visitor_type', 'all')
    industry = request.args.get('industry', 'all')
    search = request.args.get('search', '')
    
    query = Visitor.query
    
    # تصفية حسب نوع الزائر
    if visitor_type == 'company':
        query = query.filter(Visitor.company_name.isnot(None))
    elif visitor_type == 'individual':
        query = query.filter(Visitor.company_name.is_(None))
    
    # تصفية حسب القطاع
    if industry != 'all':
        query = query.filter_by(industry=industry)
    
    # البحث النصي
    if search:
        query = query.filter(or_(
            Visitor.company_name.contains(search),
            User.email.contains(search),
            User.full_name.contains(search),
            Visitor.position.contains(search)
        )).join(User)
    
    visitors = query.order_by(Visitor.created_at.desc())\
                   .paginate(page=page, per_page=20, error_out=False)
    
    # اختيار القالب المناسب حسب نوع الجهاز
    device_type = DeviceDetector.get_device_type()
    template = 'mobile/admin/visitors.html' if device_type == 'mobile' else 'admin/visitors.html'
    
    return render_template(template, 
                         visitors=visitors,
                         current_type=visitor_type,
                         current_industry=industry,
                         search_term=search)

@admin_bp.route('/visitors/<int:visitor_id>/activate', methods=['POST'])
@login_required
def activate_visitor(visitor_id):
    """تفعيل الزائر - Activate Visitor"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'غير مصرح'}), 403
    
    visitor = Visitor.query.get_or_404(visitor_id)
    visitor.is_active = True
    db.session.commit()
    
    flash(f'تم تفعيل الزائر {visitor.user.full_name}', 'success')
    return jsonify({'success': True})

@admin_bp.route('/visitors/<int:visitor_id>/deactivate', methods=['POST'])
@login_required
def deactivate_visitor(visitor_id):
    """تعطيل الزائر - Deactivate Visitor"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'غير مصرح'}), 403
    
    visitor = Visitor.query.get_or_404(visitor_id)
    visitor.is_active = False
    db.session.commit()
    
    flash(f'تم تعطيل الزائر {visitor.user.full_name}', 'warning')
    return jsonify({'success': True})

@admin_bp.route('/home-management')
@login_required
def home_management():
    """صفحة إدارة محتوى الصفحة الرئيسية - Home Page Content Management"""
    if not current_user.is_admin():
        flash('غير مصرح لك بالوصول لهذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # جلب محتوى جميع الأقسام
    from models import HomePageContent
    
    sections_data = {}
    section_names = [
        'main_banner', 'intro_video', 'pavilions', 'sponsors', 
        'featured_products', 'target_countries', 'pavilion_types', 'events'
    ]
    
    for section_name in section_names:
        content = HomePageContent.get_section(section_name)
        sections_data[f'{section_name}_content'] = content
    
    return render_device_template('admin/home_management.html', **sections_data)

@admin_bp.route('/save-home-content', methods=['POST'])
@login_required
def save_home_content():
    """حفظ محتوى قسم من الصفحة الرئيسية - Save Home Page Section Content"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'غير مصرح'}), 403
    
    try:
        from models import HomePageContent
        import json
        
        section_name = request.form.get('section_name')
        if not section_name:
            return jsonify({'success': False, 'message': 'اسم القسم مطلوب'})
        
        # البحث عن القسم الموجود أو إنشاء قسم جديد
        content = HomePageContent.query.filter_by(section_name=section_name).first()
        if not content:
            content = HomePageContent(section_name=section_name)
            db.session.add(content)
        
        # تحديث البيانات الأساسية
        content.title_ar = request.form.get('title_ar', '')
        content.title_en = request.form.get('title_en', '')
        content.description_ar = request.form.get('description_ar', '')
        content.description_en = request.form.get('description_en', '')
        content.display_order = int(request.form.get('display_order', 1))
        content.is_active = bool(request.form.get('is_active'))
        
        # معالجة الصورة الرئيسية
        if 'main_image' in request.files:
            file = request.files['main_image']
            if file and file.filename and allowed_file(file.filename):
                # إنشاء مجلد uploads/homepage إذا لم يكن موجوداً
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'homepage')
                os.makedirs(upload_folder, exist_ok=True)
                
                filename = secure_filename(f"{section_name}_{file.filename}")
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                content.main_image = f"homepage/{filename}"
        
        # معالجة معرض الصور
        if 'gallery_images' in request.files:
            files = request.files.getlist('gallery_images')
            gallery_images = []
            
            upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'homepage', 'gallery')
            os.makedirs(upload_folder, exist_ok=True)
            
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(f"{section_name}_gallery_{file.filename}")
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    gallery_images.append(f"homepage/gallery/{filename}")
            
            if gallery_images:
                content.gallery_images = json.dumps(gallery_images)
        
        # معالجة الملف المرفق
        if 'attachment_file' in request.files:
            file = request.files['attachment_file']
            if file and file.filename and allowed_file(file.filename):
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'homepage', 'attachments')
                os.makedirs(upload_folder, exist_ok=True)
                
                filename = secure_filename(f"{section_name}_{file.filename}")
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                content.attachment_file = f"homepage/attachments/{filename}"
        
        # معالجة ملف PDF
        if 'pdf_file' in request.files:
            file = request.files['pdf_file']
            if file and file.filename and file.filename.lower().endswith('.pdf'):
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'homepage', 'pdfs')
                os.makedirs(upload_folder, exist_ok=True)
                
                filename = secure_filename(f"{section_name}_{file.filename}")
                filepath = os.path.join(upload_folder, filename)
                file.save(filepath)
                content.pdf_file = f"homepage/pdfs/{filename}"
        
        # معالجة ملف الفيديو
        if 'video_file' in request.files:
            file = request.files['video_file']
            video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']
            if file and file.filename and any(file.filename.lower().endswith(ext) for ext in video_extensions):
                upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'homepage', 'videos')
                os.makedirs(upload_folder, exist_ok=True)
                
                filename = secure_filename(f"{section_name}_{file.filename}")
                filepath = os.path.join(upload_folder, filename)
                
                # حفظ الفيديو مع التعامل مع الملفات الكبيرة
                try:
                    file.save(filepath)
                    content.video_file = f"homepage/videos/{filename}"
                except Exception as e:
                    current_app.logger.error(f"Error saving video file: {str(e)}")
                    # في حالة فشل حفظ الفيديو، لا نوقف العملية بالكامل
                    pass
        
        # معالجة البيانات المخصصة
        custom_data = {}
        
        # بيانات خاصة لكل قسم
        if section_name == 'intro_video':
            custom_data['video_url'] = request.form.get('video_url', '')
        
        elif section_name == 'pavilions':
            custom_data['pavilion_count'] = int(request.form.get('pavilion_count', 0))
        
        elif section_name == 'featured_products':
            custom_data['products_count'] = int(request.form.get('products_count', 8))
            custom_data['selection_criteria'] = request.form.get('selection_criteria', 'views')
        
        elif section_name == 'target_countries':
            custom_data['countries_list'] = request.form.get('countries_list', '')
        
        elif section_name == 'pavilion_types':
            custom_data['pavilion_types_list'] = request.form.get('pavilion_types_list', '')
        
        elif section_name == 'events':
            custom_data['start_date'] = request.form.get('start_date', '')
            custom_data['end_date'] = request.form.get('end_date', '')
        
        # حفظ البيانات المخصصة
        if custom_data:
            content.set_custom_data(custom_data)
        
        # حفظ التغييرات
        content.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'تم حفظ {content.title_ar or section_name} بنجاح'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving home content: {str(e)}")
        return jsonify({
            'success': False, 
            'message': f'حدث خطأ أثناء الحفظ: {str(e)}'
        })

@admin_bp.route('/export-home-content')
@login_required
def export_home_content():
    """تصدير محتوى الصفحة الرئيسية - Export Home Page Content"""
    if not current_user.is_admin():
        flash('غير مصرح لك بالوصول لهذه الصفحة', 'error')
        return redirect(url_for('admin.dashboard'))
    
    try:
        from models import HomePageContent
        import json
        from datetime import datetime
        
        # جلب جميع محتويات الصفحة الرئيسية
        all_content = HomePageContent.query.all()
        
        export_data = {
            'export_date': datetime.utcnow().isoformat(),
            'total_sections': len(all_content),
            'sections': []
        }
        
        for content in all_content:
            section_data = {
                'section_name': content.section_name,
                'title_ar': content.title_ar,
                'title_en': content.title_en,
                'description': content.description,
                'main_image': content.main_image,
                'gallery_images': content.gallery_images,
                'attachment_file': content.attachment_file,
                'display_order': content.display_order,
                'is_active': content.is_active,
                'custom_data': content.custom_data,
                'created_at': content.created_at.isoformat() if content.created_at else None,
                'updated_at': content.updated_at.isoformat() if content.updated_at else None
            }
            export_data['sections'].append(section_data)
        
        # إنشاء استجابة JSON للتحميل
        response = jsonify(export_data)
        response.headers['Content-Disposition'] = f'attachment; filename=home_content_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        response.headers['Content-Type'] = 'application/json'
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Error exporting home content: {str(e)}")
        flash(f'حدث خطأ أثناء التصدير: {str(e)}', 'error')
        return redirect(url_for('admin.home_management'))

@admin_bp.route('/backup-home-content', methods=['POST'])
@login_required
def backup_home_content():
    """إنشاء نسخة احتياطية من محتوى الصفحة الرئيسية - Backup Home Page Content"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'غير مصرح'}), 403
    
    try:
        from models import HomePageContent
        import json
        import os
        from datetime import datetime
        
        # إنشاء مجلد النسخ الاحتياطية
        backup_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'backups', 'homepage')
        os.makedirs(backup_folder, exist_ok=True)
        
        # جلب جميع المحتويات
        all_content = HomePageContent.query.all()
        
        backup_data = {
            'backup_date': datetime.utcnow().isoformat(),
            'backup_by': current_user.email,
            'total_sections': len(all_content),
            'sections': []
        }
        
        for content in all_content:
            section_data = {
                'section_name': content.section_name,
                'title_ar': content.title_ar,
                'title_en': content.title_en,
                'description': content.description,
                'main_image': content.main_image,
                'gallery_images': content.gallery_images,
                'attachment_file': content.attachment_file,
                'display_order': content.display_order,
                'is_active': content.is_active,
                'custom_data': content.custom_data,
                'created_at': content.created_at.isoformat() if content.created_at else None,
                'updated_at': content.updated_at.isoformat() if content.updated_at else None
            }
            backup_data['sections'].append(section_data)
        
        # حفظ النسخة الاحتياطية
        backup_filename = f'homepage_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        backup_filepath = os.path.join(backup_folder, backup_filename)
        
        with open(backup_filepath, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'تم إنشاء النسخة الاحتياطية: {backup_filename}',
            'filename': backup_filename
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating backup: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'حدث خطأ أثناء إنشاء النسخة الاحتياطية: {str(e)}'
        })

# ==================== روتات إدارة الأقسام - Categories Management Routes ====================

@admin_bp.route('/categories', methods=['GET', 'POST'])
@login_required
def categories():
    """صفحة إدارة أقسام المعرض - Exhibition Categories Management"""
    if not current_user.is_admin():
        flash('غير مصرح لك بالوصول لهذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        # معالجة عمليات POST (إضافة، تعديل، حذف، تفعيل/تعطيل)
        category_id = request.form.get('category_id')
        
        if category_id:  # تعديل قسم موجود
            try:
                category = Category.query.get_or_404(int(category_id))
                
                name_ar = request.form.get('name_ar', '').strip()
                name_en = request.form.get('name_en', '').strip()
                description = request.form.get('description', '').strip()
                icon = request.form.get('icon', '').strip()
                is_active = request.form.get('is_active') == 'on'
                
                # التحقق من البيانات المطلوبة
                if not name_ar or not name_en:
                    flash('يرجى ملء الحقول المطلوبة', 'error')
                    return redirect(url_for('admin.categories'))
                
                # التحقق من عدم تكرار الاسم
                existing = Category.query.filter(
                    Category.id != category.id,
                    (Category.name_ar == name_ar) | (Category.name_en == name_en)
                ).first()
                
                if existing:
                    flash('اسم القسم موجود بالفعل', 'error')
                    return redirect(url_for('admin.categories'))
                
                # تحديث بيانات القسم
                category.name_ar = name_ar
                category.name_en = name_en
                category.description = description
                category.icon = icon
                category.is_active = is_active
                category.updated_at = datetime.utcnow()
                
                db.session.commit()
                flash(f'تم تعديل القسم "{name_ar}" بنجاح', 'success')
                
            except Exception as e:
                db.session.rollback()
                flash('حدث خطأ أثناء تعديل القسم', 'error')
                
        else:  # إضافة قسم جديد
            try:
                name_ar = request.form.get('name_ar', '').strip()
                name_en = request.form.get('name_en', '').strip()
                description = request.form.get('description', '').strip()
                icon = request.form.get('icon', '').strip()
                is_active = request.form.get('is_active') == 'on'
                
                # التحقق من البيانات المطلوبة
                if not name_ar or not name_en:
                    flash('يرجى ملء الحقول المطلوبة', 'error')
                    return redirect(url_for('admin.categories'))
                
                # التحقق من عدم تكرار الاسم
                existing = Category.query.filter(
                    (Category.name_ar == name_ar) | (Category.name_en == name_en)
                ).first()
                
                if existing:
                    flash('اسم القسم موجود بالفعل', 'error')
                    return redirect(url_for('admin.categories'))
                
                # إنشاء القسم الجديد
                category = Category(
                    name_ar=name_ar,
                    name_en=name_en,
                    description=description,
                    icon=icon,
                    is_active=is_active
                )
                db.session.add(category)
                db.session.commit()
                flash(f'تم إضافة القسم "{name_ar}" بنجاح', 'success')
                
            except Exception as e:
                db.session.rollback()
                flash('حدث خطأ أثناء إضافة القسم', 'error')
        
        return redirect(url_for('admin.categories'))
    
    # جلب جميع الأقسام مع إحصائياتها
    categories = Category.query.order_by(Category.created_at.desc()).all()
    
    # حساب الإحصائيات
    total_categories = len(categories)
    active_categories = len([c for c in categories if c.is_active])
    inactive_categories = total_categories - active_categories
    categories_with_exhibitors = len([c for c in categories if c.exhibitors])
    
    # اختيار القالب المناسب حسب نوع الجهاز
    return render_device_template('admin/categories.html', 
                                categories=categories,
                                total_categories=total_categories,
                                active_categories=active_categories,
                                inactive_categories=inactive_categories,
                                categories_with_exhibitors=categories_with_exhibitors)

@admin_bp.route('/categories/toggle/<int:category_id>', methods=['POST'])
@login_required
def toggle_category_status(category_id):
    """تفعيل/تعطيل قسم - Toggle Category Status"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'غير مصرح'}), 403
    
    try:
        category = Category.query.get_or_404(category_id)
        
        category.is_active = not category.is_active
        category.updated_at = datetime.utcnow()
        db.session.commit()
        
        status = 'تم تفعيل' if category.is_active else 'تم تعطيل'
        return jsonify({
            'success': True, 
            'message': f'{status} القسم "{category.name_ar}" بنجاح'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

@admin_bp.route('/categories/delete/<int:category_id>', methods=['POST'])
@login_required
def delete_category(category_id):
    """حذف قسم - Delete Category"""
    if not current_user.is_admin():
        return jsonify({'success': False, 'message': 'غير مصرح'}), 403
    
    try:
        category = Category.query.get_or_404(category_id)
        
        # التحقق من عدم وجود عارضين في هذا القسم
        if category.exhibitors:
            return jsonify({
                'success': False, 
                'message': 'لا يمكن حذف قسم يحتوي على عارضين'
            }), 400
        
        category_name = category.name_ar
        db.session.delete(category)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'تم حذف القسم "{category_name}" بنجاح'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'}), 500

# ==================== API Routes ====================

@api_bp.route('/search')
def search():
    """البحث في الموقع - Site Search"""
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')  # all, exhibitors, products
    
    results = {
        'exhibitors': [],
        'products': []
    }
    
    if query and len(query) >= 2:
        if search_type in ['all', 'exhibitors']:
            exhibitors = Exhibitor.query.filter(
                and_(
                    Exhibitor.registration_status == 'approved',
                    or_(
                        Exhibitor.company_name.contains(query),
                        Exhibitor.company_description.contains(query)
                    )
                )
            ).limit(10).all()
            
            results['exhibitors'] = [{
                'id': e.id,
                'name': e.company_name,
                'description': e.company_description[:100] + '...' if e.company_description else '',
                'logo': e.logo_image,
                'url': url_for('main.exhibitor_profile', exhibitor_id=e.id)
            } for e in exhibitors]
        
        if search_type in ['all', 'products']:
            products = Product.query.filter(
                and_(
                    Product.is_active == True,
                    or_(
                        Product.name.contains(query),
                        Product.description.contains(query)
                    )
                )
            ).join(Exhibitor).filter(
                Exhibitor.registration_status == 'approved'
            ).limit(10).all()
            
            results['products'] = [{
                'id': p.id,
                'name': p.name,
                'description': p.description[:100] + '...' if p.description else '',
                'image': p.main_image,
                'price': p.price,
                'currency': p.currency,
                'exhibitor': p.exhibitor.company_name,
                'url': url_for('main.product_detail', product_id=p.id)
            } for p in products]
    
    return jsonify(results)

@api_bp.route('/stats/daily')
@login_required
def daily_stats():
    """إحصائيات يومية - Daily Statistics"""
    if not current_user.is_admin():
        return jsonify({'error': 'غير مصرح'}), 403
    
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now().date() - timedelta(days=days)
    
    stats = SystemStats.query.filter(SystemStats.date >= start_date)\
                            .order_by(SystemStats.date.asc()).all()
    
    data = {
        'dates': [stat.date.strftime('%Y-%m-%d') for stat in stats],
        'new_users': [stat.new_users for stat in stats],
        'new_exhibitors': [stat.new_exhibitors for stat in stats],
        'new_visitors': [stat.new_visitors for stat in stats],
        'total_visits': [stat.total_visits for stat in stats]
    }
    
    return jsonify(data)

@api_bp.route('/register/exhibitor', methods=['POST'])
def register_exhibitor_api():
    """تسجيل عارض جديد عبر API - Register new exhibitor via API"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['companyName', 'contactPerson', 'email', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'حقل {field} مطلوب'}), 400
        
        email = data.get('email')
        
        # التحقق من وجود المستخدم
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'البريد الإلكتروني مستخدم بالفعل'}), 400
        
        # إنشاء كلمة مرور مؤقتة
        import secrets
        import string
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        
        # إنشاء المستخدم الجديد
        user = User(
            email=email,
            full_name=data.get('contactPerson'),
            phone=data.get('phone'),
            user_type='exhibitor'
        )
        user.set_password(temp_password)
        db.session.add(user)
        db.session.flush()
        
        # إنشاء ملف العارض
        exhibitor = Exhibitor(
            user_id=user.id,
            company_name=data.get('companyName'),
            contact_person=data.get('contactPerson')
        )
        db.session.add(exhibitor)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'تم إنشاء حساب العارض بنجاح! كلمة المرور المؤقتة: {temp_password}',
            'tempPassword': temp_password
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء إنشاء الحساب'}), 500

@api_bp.route('/register/visitor', methods=['POST'])
def register_visitor_api():
    """تسجيل زائر جديد عبر API - Register new visitor via API"""
    try:
        data = request.get_json()
        
        # التحقق من البيانات المطلوبة
        required_fields = ['fullName', 'email', 'phone']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'حقل {field} مطلوب'}), 400
        
        email = data.get('email')
        
        # التحقق من وجود المستخدم
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'البريد الإلكتروني مستخدم بالفعل'}), 400
        
        # إنشاء كلمة مرور مؤقتة
        import secrets
        import string
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
        
        # إنشاء المستخدم الجديد
        user = User(
            email=email,
            full_name=data.get('fullName'),
            phone=data.get('phone'),
            user_type='visitor'
        )
        user.set_password(temp_password)
        db.session.add(user)
        db.session.flush()
        
        # إنشاء ملف الزائر
        visitor = Visitor(user_id=user.id)
        db.session.add(visitor)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'تم إنشاء حساب الزائر بنجاح! كلمة المرور المؤقتة: {temp_password}',
            'tempPassword': temp_password
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'حدث خطأ أثناء إنشاء الحساب'}), 500

# ==================== دوال مساعدة - Helper Functions ====================

def register_blueprints(app):
    """تسجيل جميع البلو برينتس - Register all blueprints"""
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(exhibitor_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
