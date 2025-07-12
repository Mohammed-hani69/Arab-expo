# -*- coding: utf-8 -*-
"""
كاشف الأجهزة - Device Detector
يحدد نوع الجهاز (موبايل/ديسكتوب) ويوجه المستخدم للصفحة المناسبة
"""

import re
from flask import request

class DeviceDetector:
    
    # قائمة User Agents للأجهزة المحمولة
    MOBILE_USER_AGENTS = [
        r'Mobile', r'Android', r'iPhone', r'iPod',
        r'BlackBerry', r'Windows Phone', r'Opera Mini',
        r'IEMobile', r'Mobile Safari', r'webOS', r'Kindle',
        r'Nokia', r'Samsung', r'HTC', r'LG', r'Sony',
        r'Motorola', r'Xiaomi', r'Huawei', r'OnePlus'
    ]
    
    # قائمة User Agents للأجهزة اللوحية (تعامل كديسكتوب)
    TABLET_USER_AGENTS = [
        r'iPad', r'Android.*Tablet', r'Kindle', r'Silk',
        r'PlayBook', r'Tablet', r'Galaxy Tab'
    ]
    
    @staticmethod
    def is_mobile():
        """التحقق من كون الجهاز محمولاً - Check if device is mobile"""
        user_agent = request.headers.get('User-Agent', '')
        
        # التحقق من عرض الشاشة إذا متوفر
        accept = request.headers.get('Accept', '')
        
        # قواعد التحقق من الموبايل
        mobile_patterns = [
            r'Mobile', r'Android(?!.*Tablet)', r'iPhone', r'iPod',
            r'BlackBerry', r'Windows Phone', r'Opera Mini',
            r'IEMobile', r'Mobile Safari', r'webOS'
        ]
        
        for pattern in mobile_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def is_tablet():
        """التحقق من كون الجهاز لوحياً - Check if device is tablet"""
        user_agent = request.headers.get('User-Agent', '')
        
        tablet_patterns = [
            r'iPad', r'Android.*Tablet', r'Kindle', r'Silk',
            r'PlayBook', r'Tablet', r'Galaxy Tab'
        ]
        
        for pattern in tablet_patterns:
            if re.search(pattern, user_agent, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def is_desktop():
        """التحقق من كون الجهاز ديسكتوب - Check if device is desktop"""
        return not DeviceDetector.is_mobile()
    
    @staticmethod
    def get_device_type():
        """جلب نوع الجهاز - Get device type"""
        if DeviceDetector.is_mobile():
            return 'mobile'
        elif DeviceDetector.is_tablet():
            return 'tablet'  # نعامل التابلت كديسكتوب
        else:
            return 'desktop'
    
    @staticmethod
    def get_template_path(base_template):
        """الحصول على مسار القالب المناسب - Get appropriate template path"""
        device_type = DeviceDetector.get_device_type()
        
        if device_type == 'mobile':
            # للموبايل: استخدم مجلد mobile
            if not base_template.startswith('mobile/'):
                base_template = f'mobile/{base_template}'
        
        return base_template
    
    @staticmethod
    def should_redirect_to_mobile():
        """تحديد ما إذا كان يجب التوجيه للموبايل - Determine if should redirect to mobile"""
        return DeviceDetector.get_device_type() == 'mobile'
