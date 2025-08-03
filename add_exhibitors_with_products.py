# -*- coding: u    {
        'user_info': {
            'email': 'info@al-noor-dairy.sa',
            'password': 'AlNoor123!',
            'full_name': 'Ahmed Al-Noor',
            'phone': '+966501234567'
        },
"""
سكريبت إضافة عارضين جدد مع منتجاتهم
Script to Add New Exhibitors with Their Products
"""

from app import app
from models import db, User, Exhibitor, Product, Category
from werkzeug.security import generate_password_hash
import random
import json
import datetime

# قائمة العارضين الجدد مع معلوماتهم - New Exhibitors Information
SAMPLE_EXHIBITORS = [
    {
        'user_info': {
            'username': 'al_noor_dairy',
            'email': 'info@alnoor-dairy.com',
            'password': 'Alnoor123!',
            'full_name': 'Ahmed Al-Noor',
            'phone': '+966501234567'
        },
        'exhibitor_info': {
            'company_name': 'Al-Noor Dairy Products',
            'company_description': 'Premium dairy products manufacturer specializing in fresh milk, artisanal cheeses, and organic dairy items sourced from local farms across Saudi Arabia.',
            'country': 'Saudi Arabia',
            'city': 'Riyadh',
            'company_website': 'https://alnoor-dairy.com',
            'category_name': 'Dairy Products',
            'booth_size': 'Large',
            'booth_type': 'Premium'
        },
        'products_category': 'dairy'
    },
    {
        'user_info': {
            'username': 'emirates_spices',
            'email': 'contact@emirates-spices.ae',
            'password': 'Emirates123!',
            'full_name': 'Fatima Al-Zahra',
            'phone': '+971501234567'
        },
        'exhibitor_info': {
            'company_name': 'Emirates Premium Spices',
            'company_description': 'Leading supplier of authentic Middle Eastern and international spices, herbs, and seasonings. We source the finest quality spices from around the world.',
            'country': 'United Arab Emirates',
            'city': 'Dubai',
            'company_website': 'https://emirates-spices.ae',
            'category_name': 'Spices & Herbs',
            'booth_size': 'Medium',
            'booth_type': 'Standard'
        },
        'products_category': 'spices'
    },
    {
        'user_info': {
            'username': 'nile_fruits',
            'email': 'sales@nile-fruits.eg',
            'password': 'Nile123!',
            'full_name': 'Mohamed Hassan',
            'phone': '+201234567890'
        },
        'exhibitor_info': {
            'company_name': 'Nile Valley Fresh Fruits',
            'company_description': 'Egypt\'s premier fresh fruit exporter, specializing in citrus fruits, dates, and tropical fruits grown in the fertile Nile Delta region.',
            'country': 'Egypt',
            'city': 'Cairo',
            'company_website': 'https://nile-fruits.eg',
            'category_name': 'Fresh Fruits',
            'booth_size': 'Large',
            'booth_type': 'Premium'
        },
        'products_category': 'fruits'
    },
    {
        'user_info': {
            'username': 'levant_bakery',
            'email': 'info@levant-bakery.jo',
            'password': 'Levant123!',
            'full_name': 'Omar Al-Rashid',
            'phone': '+962791234567'
        },
        'exhibitor_info': {
            'company_name': 'Levant Traditional Bakery',
            'company_description': 'Authentic Middle Eastern bakery specializing in traditional breads, pastries, and baked goods using time-honored recipes and premium ingredients.',
            'country': 'Jordan',
            'city': 'Amman',
            'company_website': 'https://levant-bakery.jo',
            'category_name': 'Bakery & Pastries',
            'booth_size': 'Medium',
            'booth_type': 'Standard'
        },
        'products_category': 'bakery'
    },
    {
        'user_info': {
            'username': 'gulf_seafood',
            'email': 'orders@gulf-seafood.kw',
            'password': 'Gulf123!',
            'full_name': 'Ali Al-Sabah',
            'phone': '+96550123456'
        },
        'exhibitor_info': {
            'company_name': 'Gulf Premium Seafood',
            'company_description': 'Fresh seafood supplier from the Arabian Gulf, offering the finest selection of fish, shrimp, and other marine products caught from pristine waters.',
            'country': 'Kuwait',
            'city': 'Kuwait City',
            'company_website': 'https://gulf-seafood.kw',
            'category_name': 'Seafood',
            'booth_size': 'Large',
            'booth_type': 'Premium'
        },
        'products_category': 'seafood'
    },
    {
        'user_info': {
            'username': 'moroccan_olives',
            'email': 'info@moroccan-olives.ma',
            'password': 'Morocco123!',
            'full_name': 'Aicha Benali',
            'phone': '+212612345678'
        },
        'exhibitor_info': {
            'company_name': 'Moroccan Gold Olives',
            'company_description': 'Premium olive oil and olive products from the Atlas Mountains of Morocco. We specialize in extra virgin olive oil and gourmet olive varieties.',
            'country': 'Morocco',
            'city': 'Casablanca',
            'company_website': 'https://moroccan-olives.ma',
            'category_name': 'Oils & Condiments',
            'booth_size': 'Medium',
            'booth_type': 'Standard'
        },
        'products_category': 'general'
    }
]

# قائمة أسماء المنتجات العربية والإنجليزية - Arabic and English Product Names
SAMPLE_PRODUCTS = {
    'dairy': [
        {'name': 'Fresh Milk', 'name_ar': 'حليب طازج', 'description': 'Pure and fresh daily milk from local farms', 'description_ar': 'حليب طازج ونقي من المزارع المحلية', 'price_range': (2.5, 5.0)},
        {'name': 'Greek Yogurt', 'name_ar': 'لبن زبادي يوناني', 'description': 'Creamy Greek yogurt with natural probiotics', 'description_ar': 'لبن زبادي يوناني كريمي بالبروبيوتيك الطبيعي', 'price_range': (3.0, 6.5)},
        {'name': 'Aged Cheese', 'name_ar': 'جبن معتق', 'description': 'Premium aged cheese with rich flavor', 'description_ar': 'جبن معتق فاخر بنكهة غنية', 'price_range': (8.0, 25.0)},
        {'name': 'Butter', 'name_ar': 'زبدة طبيعية', 'description': 'Natural butter made from cream', 'description_ar': 'زبدة طبيعية مصنوعة من الكريمة', 'price_range': (4.0, 8.0)},
        {'name': 'Cream Cheese', 'name_ar': 'جبن كريمي', 'description': 'Soft cream cheese perfect for spreads', 'description_ar': 'جبن كريمي ناعم مثالي للدهن', 'price_range': (3.5, 7.0)},
        {'name': 'Mozzarella', 'name_ar': 'جبن موتزاريلا', 'description': 'Fresh mozzarella cheese', 'description_ar': 'جبن موتزاريلا طازج', 'price_range': (5.0, 12.0)},
        {'name': 'Labneh', 'name_ar': 'لبنة طبيعية', 'description': 'Traditional Middle Eastern strained yogurt', 'description_ar': 'لبنة شرق أوسطية تقليدية', 'price_range': (3.0, 7.0)},
    ],
    'spices': [
        {'name': 'Saffron', 'name_ar': 'زعفران أصلي', 'description': 'Premium saffron threads from Iran', 'description_ar': 'خيوط زعفران فاخرة من إيران', 'price_range': (50.0, 150.0)},
        {'name': 'Cardamom', 'name_ar': 'هيل أخضر', 'description': 'Green cardamom pods', 'description_ar': 'حبات هيل أخضر', 'price_range': (15.0, 30.0)},
        {'name': 'Cinnamon', 'name_ar': 'قرفة سيلانية', 'description': 'Ceylon cinnamon sticks', 'description_ar': 'أعواد قرفة سيلانية', 'price_range': (8.0, 18.0)},
        {'name': 'Black Pepper', 'name_ar': 'فلفل أسود مطحون', 'description': 'Freshly ground black pepper', 'description_ar': 'فلفل أسود مطحون طازج', 'price_range': (5.0, 12.0)},
        {'name': 'Turmeric', 'name_ar': 'كركم طبيعي', 'description': 'Organic turmeric powder', 'description_ar': 'مسحوق كركم عضوي', 'price_range': (3.0, 8.0)},
        {'name': 'Sumac', 'name_ar': 'سماق حامض', 'description': 'Tangy sumac spice', 'description_ar': 'سماق حامض طبيعي', 'price_range': (6.0, 12.0)},
        {'name': 'Za\'atar', 'name_ar': 'زعتر بلدي', 'description': 'Traditional Middle Eastern herb blend', 'description_ar': 'خلطة زعتر شرق أوسطية تقليدية', 'price_range': (4.0, 10.0)},
    ],
    'fruits': [
        {'name': 'Organic Dates', 'name_ar': 'تمر عضوي', 'description': 'Premium Medjool dates from Saudi Arabia', 'description_ar': 'تمر مجهول فاخر من السعودية', 'price_range': (8.0, 20.0)},
        {'name': 'Fresh Oranges', 'name_ar': 'برتقال طازج', 'description': 'Juicy Valencia oranges', 'description_ar': 'برتقال فالنسيا عصيري', 'price_range': (2.0, 5.0)},
        {'name': 'Pomegranates', 'name_ar': 'رمان طازج', 'description': 'Sweet and tangy pomegranates', 'description_ar': 'رمان حلو وحامض', 'price_range': (4.0, 8.0)},
        {'name': 'Mangoes', 'name_ar': 'مانجو استوائية', 'description': 'Tropical mangoes with rich flavor', 'description_ar': 'مانجو استوائية بنكهة غنية', 'price_range': (3.0, 10.0)},
        {'name': 'Grapes', 'name_ar': 'عنب طازج', 'description': 'Sweet seedless grapes', 'description_ar': 'عنب حلو بدون بذور', 'price_range': (3.5, 7.0)},
        {'name': 'Figs', 'name_ar': 'تين طازج', 'description': 'Fresh Mediterranean figs', 'description_ar': 'تين البحر المتوسط الطازج', 'price_range': (5.0, 12.0)},
        {'name': 'Lemons', 'name_ar': 'ليمون حامض', 'description': 'Fresh lemons with intense flavor', 'description_ar': 'ليمون حامض بنكهة قوية', 'price_range': (1.5, 4.0)},
    ],
    'bakery': [
        {'name': 'Arabic Bread', 'name_ar': 'خبز عربي طازج', 'description': 'Fresh traditional Arabic flatbread', 'description_ar': 'خبز عربي تقليدي طازج', 'price_range': (1.0, 3.0)},
        {'name': 'Pita Bread', 'name_ar': 'خبز البيتا', 'description': 'Soft and fluffy pita bread', 'description_ar': 'خبز بيتا ناعم ومنفوش', 'price_range': (1.5, 3.5)},
        {'name': 'Manakish', 'name_ar': 'مناقيش بالزعتر', 'description': 'Traditional flatbread with za\'atar', 'description_ar': 'خبز تقليدي بالزعتر', 'price_range': (2.0, 5.0)},
        {'name': 'Baklava', 'name_ar': 'بقلاوة شرقية', 'description': 'Traditional Middle Eastern pastry with nuts and honey', 'description_ar': 'معجنات شرق أوسطية تقليدية بالمكسرات والعسل', 'price_range': (8.0, 20.0)},
        {'name': 'Croissants', 'name_ar': 'كرواسون فرنسي', 'description': 'Buttery French croissants', 'description_ar': 'كرواسون فرنسي بالزبدة', 'price_range': (2.0, 5.0)},
        {'name': 'Cookies', 'name_ar': 'بسكويت محلي الصنع', 'description': 'Homemade cookies with natural ingredients', 'description_ar': 'بسكويت محلي الصنع بمكونات طبيعية', 'price_range': (3.5, 8.0)},
    ],
    'seafood': [
        {'name': 'Fresh Salmon', 'name_ar': 'سلمون طازج', 'description': 'Wild-caught Atlantic salmon', 'description_ar': 'سلمون الأطلسي المصطاد طبيعياً', 'price_range': (18.0, 35.0)},
        {'name': 'Gulf Shrimp', 'name_ar': 'جمبري الخليج', 'description': 'Fresh jumbo shrimp from Arabian Gulf', 'description_ar': 'جمبري جامبو طازج من الخليج العربي', 'price_range': (25.0, 45.0)},
        {'name': 'Sea Bass', 'name_ar': 'سمك القاروص', 'description': 'Mediterranean sea bass', 'description_ar': 'سمك قاروص البحر المتوسط', 'price_range': (16.0, 28.0)},
        {'name': 'Red Snapper', 'name_ar': 'سمك الهامور الأحمر', 'description': 'Fresh red snapper from Gulf waters', 'description_ar': 'سمك هامور أحمر طازج من مياه الخليج', 'price_range': (20.0, 38.0)},
        {'name': 'Tuna Steaks', 'name_ar': 'شرائح التونة', 'description': 'Fresh tuna steaks for grilling', 'description_ar': 'شرائح تونة طازجة للشوي', 'price_range': (25.0, 45.0)},
        {'name': 'Crab', 'name_ar': 'سرطان البحر', 'description': 'Fresh crab from coastal waters', 'description_ar': 'سرطان بحر طازج من المياه الساحلية', 'price_range': (30.0, 55.0)},
    ],
    'general': [
        {'name': 'Olive Oil', 'name_ar': 'زيت الزيتون البكر', 'description': 'Extra virgin olive oil', 'description_ar': 'زيت زيتون بكر ممتاز', 'price_range': (12.0, 30.0)},
        {'name': 'Honey', 'name_ar': 'عسل طبيعي', 'description': 'Pure natural honey', 'description_ar': 'عسل طبيعي صافي', 'price_range': (8.0, 25.0)},
        {'name': 'Vinegar', 'name_ar': 'خل بلسمي', 'description': 'Aged balsamic vinegar', 'description_ar': 'خل بلسمي معتق', 'price_range': (6.0, 18.0)},
        {'name': 'Pickles', 'name_ar': 'مخللات مشكلة', 'description': 'Mixed pickled vegetables', 'description_ar': 'مخللات خضار مشكلة', 'price_range': (3.0, 8.0)},
        {'name': 'Jam', 'name_ar': 'مربى طبيعي', 'description': 'Natural fruit preserves', 'description_ar': 'مربى فواكه طبيعي', 'price_range': (4.0, 12.0)},
    ]
}

# قائمة العلامات/التاجز - Tags list
PRODUCT_TAGS = {
    'general': ['حلال', 'عضوي', 'طبيعي', 'طازج', 'فاخر', 'محلي', 'مستورد'],
    'dietary': ['خالي من الجلوتين', 'نباتي', 'قليل الدسم', 'غني بالبروتين', 'خالي من السكر'],
    'certifications': ['ISO معتمد', 'HACCP', 'BRC معتمد', 'معتمد دولياً']
}

def get_random_tags():
    """الحصول على علامات عشوائية - Get random tags"""
    all_tags = []
    for category in PRODUCT_TAGS.values():
        all_tags.extend(category)
    
    num_tags = random.randint(2, 5)
    selected_tags = random.sample(all_tags, min(num_tags, len(all_tags)))
    return json.dumps(selected_tags)

def get_or_create_category(category_name):
    """الحصول على الفئة أو إنشاؤها - Get or create category"""
    category = Category.query.filter_by(name_en=category_name).first()
    if not category:
        # إنشاء فئة جديدة
        category_mapping = {
            'Dairy Products': {'name_ar': 'منتجات الألبان', 'icon': 'fas fa-cheese'},
            'Spices & Herbs': {'name_ar': 'التوابل والأعشاب', 'icon': 'fas fa-seedling'},
            'Fresh Fruits': {'name_ar': 'الفواكه الطازجة', 'icon': 'fas fa-apple-alt'},
            'Bakery & Pastries': {'name_ar': 'المخبوزات والمعجنات', 'icon': 'fas fa-bread-slice'},
            'Seafood': {'name_ar': 'المأكولات البحرية', 'icon': 'fas fa-fish'},
            'Oils & Condiments': {'name_ar': 'الزيوت والتوابل', 'icon': 'fas fa-oil-can'}
        }
        
        mapping = category_mapping.get(category_name, {
            'name_ar': category_name,
            'icon': 'fas fa-box'
        })
        
        category = Category(
            name_en=category_name,
            name_ar=mapping['name_ar'],
            icon=mapping['icon'],
            description=f'Category for {category_name}',
            is_active=True
        )
        db.session.add(category)
        db.session.flush()  # للحصول على ID الفئة
    
    return category

def create_user_and_exhibitor(exhibitor_data):
    """إنشاء مستخدم وعارض جديد - Create new user and exhibitor"""
    user_info = exhibitor_data['user_info']
    exhibitor_info = exhibitor_data['exhibitor_info']
    
    # التحقق من وجود المستخدم
    existing_user = User.query.filter_by(email=user_info['email']).first()
    
    if existing_user:
        print(f"⚠️ المستخدم {user_info['email']} موجود بالفعل")
        print(f"⚠️ User {user_info['email']} already exists")
        return None
    
    # إنشاء المستخدم
    user = User(
        email=user_info['email'],
        full_name=user_info['full_name'],
        phone=user_info['phone'],
        user_type='exhibitor',
        is_active=True
    )
    user.set_password(user_info['password'])
    
    db.session.add(user)
    db.session.flush()  # للحصول على ID المستخدم
    
    # الحصول على الفئة أو إنشاؤها
    category = get_or_create_category(exhibitor_info['category_name'])
    
    # إنشاء العارض
    exhibitor = Exhibitor(
        user_id=user.id,
        category_id=category.id,
        company_name=exhibitor_info['company_name'],
        company_description=exhibitor_info['company_description'],
        country=exhibitor_info['country'],
        city=exhibitor_info['city'],
        company_website=exhibitor_info['company_website'],
        booth_size=exhibitor_info['booth_size'],
        booth_type=exhibitor_info['booth_type'],
        registration_status='approved',
        payment_status='paid',
        profile_views=random.randint(50, 500),
        total_products=0
    )
    
    db.session.add(exhibitor)
    db.session.flush()  # للحصول على ID العارض
    
    return exhibitor

def add_products_to_exhibitor(exhibitor, category_products):
    """إضافة منتجات للعارض - Add products to exhibitor"""
    # عدد المنتجات العشوائي بين 5 و 10 - Random number of products between 5 and 10
    num_products = random.randint(5, 10)
    
    # اختيار منتجات عشوائية - Select random products
    if len(category_products) >= num_products:
        selected_products = random.sample(category_products, num_products)
    else:
        # إذا كانت المنتجات قليلة، كرر بعضها مع تغيير الأسماء
        selected_products = category_products * (num_products // len(category_products) + 1)
        selected_products = selected_products[:num_products]
    
    products_added = 0
    
    for i, product_data in enumerate(selected_products):
        try:
            # إنشاء اسم فريد للمنتج
            base_name = product_data['name']
            if i > 0 and len(category_products) < num_products:
                base_name += f" - Variety {i+1}"
            
            # حساب السعر العشوائي ضمن النطاق
            min_price, max_price = product_data['price_range']
            price = round(random.uniform(min_price, max_price), 2)
            
            # إنشاء المنتج
            product = Product(
                exhibitor_id=exhibitor.id,
                name=base_name,
                description=product_data['description'],
                price=price,
                currency='USD',
                category=exhibitor.category.name_en if exhibitor.category else 'Other',
                tags=get_random_tags(),
                is_active=True,
                is_featured=random.choice([True, False]) if random.random() < 0.3 else False,  # 30% chance to be featured
                views_count=random.randint(0, 500),
                inquiries_count=random.randint(0, 50)
            )
            
            db.session.add(product)
            products_added += 1
            
        except Exception as e:
            print(f"❌ خطأ في إضافة المنتج {product_data['name']}: {str(e)}")
            print(f"❌ Error adding product {product_data['name']}: {str(e)}")
            continue
    
    # تحديث عدد المنتجات الكلي للعارض
    exhibitor.total_products = products_added
    
    return products_added

def main():
    """الدالة الرئيسية - Main function"""
    with app.app_context():
        print("🚀 بدء إضافة العارضين الجدد مع منتجاتهم...")
        print("🚀 Starting to add new exhibitors with their products...")
        
        total_exhibitors_added = 0
        total_products_added = 0
        
        for exhibitor_data in SAMPLE_EXHIBITORS:
            print(f"\n🏢 إضافة العارض: {exhibitor_data['exhibitor_info']['company_name']}")
            print(f"🏢 Adding exhibitor: {exhibitor_data['exhibitor_info']['company_name']}")
            
            try:
                # إنشاء المستخدم والعارض
                exhibitor = create_user_and_exhibitor(exhibitor_data)
                
                if not exhibitor:
                    continue
                
                total_exhibitors_added += 1
                
                # إضافة المنتجات
                products_category = exhibitor_data['products_category']
                category_products = SAMPLE_PRODUCTS.get(products_category, SAMPLE_PRODUCTS['general'])
                
                products_added = add_products_to_exhibitor(exhibitor, category_products)
                total_products_added += products_added
                
                print(f"   ✅ تم إنشاء العارض بنجاح")
                print(f"   ✅ Exhibitor created successfully")
                print(f"   📦 تم إضافة {products_added} منتج")
                print(f"   📦 Added {products_added} products")
                
            except Exception as e:
                print(f"❌ خطأ في إضافة العارض {exhibitor_data['exhibitor_info']['company_name']}: {str(e)}")
                print(f"❌ Error adding exhibitor {exhibitor_data['exhibitor_info']['company_name']}: {str(e)}")
                continue
        
        # حفظ التغييرات
        try:
            db.session.commit()
            print(f"\n🎉 تم الانتهاء بنجاح!")
            print(f"🎉 Successfully completed!")
            print(f"👥 إجمالي العارضين المضافين: {total_exhibitors_added}")
            print(f"👥 Total exhibitors added: {total_exhibitors_added}")
            print(f"📈 إجمالي المنتجات المضافة: {total_products_added}")
            print(f"📈 Total products added: {total_products_added}")
            if total_exhibitors_added > 0:
                print(f"📊 معدل المنتجات لكل عارض: {total_products_added/total_exhibitors_added:.1f}")
                print(f"📊 Average products per exhibitor: {total_products_added/total_exhibitors_added:.1f}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطأ في حفظ البيانات: {str(e)}")
            print(f"❌ Error saving data: {str(e)}")

if __name__ == "__main__":
    main()
