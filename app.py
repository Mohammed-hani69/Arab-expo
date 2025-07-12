# -*- coding: utf-8 -*-
"""
تطبيق معرض الطعام العربي
Arab Expo For Food Application
"""

from flask import Flask, render_template, request, flash
from flask_login import LoginManager
import os
from datetime import timedelta

# استيراد النماذج والروتات
from models import init_db, User
from routes import register_blueprints
from device_detector import DeviceDetector

def create_app():
    """إنشاء تطبيق Flask - Create Flask Application"""
    app = Flask(__name__)
    
    # إعدادات التطبيق - Application Configuration
    app.config['SECRET_KEY'] = 'arab-expo-food-2025-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///arab_expo.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # إعدادات رفع الملفات - File Upload Configuration
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 2 * 1024 * 1024 * 1024  # 2GB max file size for videos
    
    # إعدادات الجلسة - Session Configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    app.config['SESSION_COOKIE_SECURE'] = False  # True في الإنتاج مع HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # تهيئة قاعدة البيانات - Initialize Database
    init_db(app)
    
    # تهيئة نظام تسجيل الدخول - Initialize Login Manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول لهذه الصفحة'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        """تحميل المستخدم - Load User"""
        return User.query.get(int(user_id))
    
    # تسجيل الروتات - Register Routes
    register_blueprints(app)
    
    # إنشاء مجلدات الرفع - Create Upload Directories
    upload_folders = [
        'static/uploads',
        'static/uploads/exhibitors',
        'static/uploads/products',
        'static/uploads/temp'
    ]
    
    for folder in upload_folders:
        folder_path = os.path.join(app.root_path, folder)
        os.makedirs(folder_path, exist_ok=True)
    
    # معالج الأخطاء - Error Handlers
    @app.errorhandler(404)
    def not_found_error(error):
        from routes import render_device_template
        return render_device_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from routes import render_device_template
        return render_device_template('errors/500.html'), 500
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        from routes import render_device_template
        flash('الملف المرفوع كبير جداً. الحد الأقصى المسموح به هو 2 جيجابايت.', 'error')
        return render_device_template('errors/413.html'), 413
    
    # دوال مساعدة لكشف الجهاز - Device Detection Helper Functions
    @app.template_global()
    def is_mobile():
        """التحقق من كون الجهاز محمولاً - Check if device is mobile"""
        return DeviceDetector.is_mobile()
    
    @app.template_global()
    def is_desktop():
        """التحقق من كون الجهاز ديسكتوب - Check if device is desktop"""
        return DeviceDetector.is_desktop()
    
    @app.template_global()
    def get_device_type():
        """جلب نوع الجهاز - Get device type"""
        return DeviceDetector.get_device_type()
    
    # دوال مساعدة للقوالب - Template Helper Functions
    @app.template_filter('currency')
    def currency_filter(amount, currency='USD'):
        """تنسيق العملة - Format Currency"""
        if amount is None:
            return 'غير محدد'
        
        symbols = {
            'USD': '$',
            'EUR': '€',
            'SAR': 'ر.س',
            'AED': 'د.إ',
            'EGP': 'ج.م'
        }
        
        symbol = symbols.get(currency, currency)
        return f"{amount:,.2f} {symbol}"
    
    @app.template_filter('from_json')
    def from_json_filter(json_string):
        """تحويل JSON إلى قائمة - Convert JSON to List"""
        if not json_string:
            return []
        try:
            import json
            return json.loads(json_string)
        except:
            return []

    @app.template_filter('timeago')
    def timeago_filter(datetime_obj):
        """عرض الوقت النسبي - Display Relative Time"""
        if not datetime_obj:
            return ''
        
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        diff = now - datetime_obj
        
        if diff.days > 0:
            return f"منذ {diff.days} يوم"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"منذ {hours} ساعة"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"منذ {minutes} دقيقة"
        else:
            return "منذ لحظات"
    
    @app.template_global()
    def get_categories():
        """الحصول على جميع الأقسام - Get All Categories"""
        from models import Category
        return Category.query.filter_by(is_active=True).all()
    
    return app

# إنشاء التطبيق - Create Application
app = create_app()

if __name__ == '__main__':
    # تشغيل التطبيق - Run Application
    print("🚀 بدء تشغيل معرض الطعام العربي...")
    print("📱 الموقع متاح على: http://localhost:5000")
    print("👨‍💼 لوحة الإدارة: http://localhost:5000/admin")
    print("📧 المستخدم الإداري: admin@arabexpo.com / admin123")
    
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000,
        threaded=True
    )
