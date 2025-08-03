# -*- coding: utf-8 -*-
"""
سكريبت إضافة منتجات عينة للعارضين الموجودين
Script to Add Sample Products for Existing Exhibitors
"""

from app import app
from models import db, Exhibitor, Product, Category
import random
import json

# إعدادات المنتجات - Product Settings
PRODUCTS_PER_EXHIBITOR_MIN = 5  # الحد الأدنى للمنتجات لكل عارض
PRODUCTS_PER_EXHIBITOR_MAX = 15  # الحد الأقصى للمنتجات لكل عارض

# قائمة أسماء المنتجات العربية والإنجليزية - Arabic and English Product Names
SAMPLE_PRODUCTS = {
    'dairy': [
        {'name': 'Fresh Milk', 'name_ar': 'حليب طازج', 'description': 'Pure and fresh daily milk from local farms', 'description_ar': 'حليب طازج ونقي من المزارع المحلية', 'price_range': (2.5, 5.0)},
        {'name': 'Greek Yogurt', 'name_ar': 'لبن زبادي يوناني', 'description': 'Creamy Greek yogurt with natural probiotics', 'description_ar': 'لبن زبادي يوناني كريمي بالبروبيوتيك الطبيعي', 'price_range': (3.0, 6.5)},
        {'name': 'Aged Cheese', 'name_ar': 'جبن معتق', 'description': 'Premium aged cheese with rich flavor', 'description_ar': 'جبن معتق فاخر بنكهة غنية', 'price_range': (8.0, 25.0)},
        {'name': 'Butter', 'name_ar': 'زبدة طبيعية', 'description': 'Natural butter made from cream', 'description_ar': 'زبدة طبيعية مصنوعة من الكريمة', 'price_range': (4.0, 8.0)},
        {'name': 'Cream Cheese', 'name_ar': 'جبن كريمي', 'description': 'Soft cream cheese perfect for spreads', 'description_ar': 'جبن كريمي ناعم مثالي للدهن', 'price_range': (3.5, 7.0)},
    ],
    'meat': [
        {'name': 'Premium Beef', 'name_ar': 'لحم بقري فاخر', 'description': 'High-quality grass-fed beef cuts', 'description_ar': 'قطع لحم بقري عالي الجودة من الأبقار المرعية', 'price_range': (15.0, 45.0)},
        {'name': 'Organic Chicken', 'name_ar': 'دجاج عضوي', 'description': 'Free-range organic chicken', 'description_ar': 'دجاج عضوي من المراعي الحرة', 'price_range': (8.0, 18.0)},
        {'name': 'Lamb Chops', 'name_ar': 'قطع لحم خروف', 'description': 'Tender lamb chops from local farms', 'description_ar': 'قطع لحم خروف طرية من المزارع المحلية', 'price_range': (20.0, 35.0)},
        {'name': 'Turkey Breast', 'name_ar': 'صدر ديك رومي', 'description': 'Lean turkey breast meat', 'description_ar': 'لحم صدر ديك رومي قليل الدهن', 'price_range': (12.0, 22.0)},
        {'name': 'Sausages', 'name_ar': 'سجق طبيعي', 'description': 'Natural sausages with herbs and spices', 'description_ar': 'سجق طبيعي بالأعشاب والتوابل', 'price_range': (6.0, 15.0)},
    ],
    'seafood': [
        {'name': 'Fresh Salmon', 'name_ar': 'سلمون طازج', 'description': 'Wild-caught Atlantic salmon', 'description_ar': 'سلمون الأطلسي المصطاد طبيعياً', 'price_range': (18.0, 35.0)},
        {'name': 'Shrimp', 'name_ar': 'جمبري طازج', 'description': 'Fresh jumbo shrimp from clean waters', 'description_ar': 'جمبري جامبو طازج من المياه النظيفة', 'price_range': (22.0, 40.0)},
        {'name': 'Sea Bass', 'name_ar': 'سمك القاروص', 'description': 'Mediterranean sea bass', 'description_ar': 'سمك قاروص البحر المتوسط', 'price_range': (16.0, 28.0)},
        {'name': 'Tuna Steaks', 'name_ar': 'شرائح التونة', 'description': 'Fresh tuna steaks for grilling', 'description_ar': 'شرائح تونة طازجة للشوي', 'price_range': (25.0, 45.0)},
        {'name': 'Crab', 'name_ar': 'سرطان البحر', 'description': 'Fresh crab from coastal waters', 'description_ar': 'سرطان بحر طازج من المياه الساحلية', 'price_range': (30.0, 55.0)},
    ],
    'fruits': [
        {'name': 'Organic Dates', 'name_ar': 'تمر عضوي', 'description': 'Premium Medjool dates from Saudi Arabia', 'description_ar': 'تمر مجهول فاخر من السعودية', 'price_range': (8.0, 20.0)},
        {'name': 'Fresh Oranges', 'name_ar': 'برتقال طازج', 'description': 'Juicy Valencia oranges', 'description_ar': 'برتقال فالنسيا عصيري', 'price_range': (2.0, 5.0)},
        {'name': 'Pomegranates', 'name_ar': 'رمان طازج', 'description': 'Sweet and tangy pomegranates', 'description_ar': 'رمان حلو وحامض', 'price_range': (4.0, 8.0)},
        {'name': 'Mangoes', 'name_ar': 'مانجو استوائية', 'description': 'Tropical mangoes with rich flavor', 'description_ar': 'مانجو استوائية بنكهة غنية', 'price_range': (3.0, 10.0)},
        {'name': 'Grapes', 'name_ar': 'عنب طازج', 'description': 'Sweet seedless grapes', 'description_ar': 'عنب حلو بدون بذور', 'price_range': (3.5, 7.0)},
        {'name': 'Figs', 'name_ar': 'تين طازج', 'description': 'Fresh Mediterranean figs', 'description_ar': 'تين البحر المتوسط الطازج', 'price_range': (5.0, 12.0)},
        {'name': 'Lemons', 'name_ar': 'ليمون حامض', 'description': 'Fresh lemons with intense flavor', 'description_ar': 'ليمون حامض بنكهة قوية', 'price_range': (1.5, 4.0)},
        {'name': 'Bananas', 'name_ar': 'موز طازج', 'description': 'Fresh tropical bananas', 'description_ar': 'موز استوائي طازج', 'price_range': (1.8, 4.5)},
    ],
    'vegetables': [
        {'name': 'Organic Tomatoes', 'name_ar': 'طماطم عضوية', 'description': 'Vine-ripened organic tomatoes', 'description_ar': 'طماطم عضوية نضجت على الشجرة', 'price_range': (2.5, 5.0)},
        {'name': 'Fresh Cucumbers', 'name_ar': 'خيار طازج', 'description': 'Crisp fresh cucumbers', 'description_ar': 'خيار طازج ومقرمش', 'price_range': (1.5, 3.0)},
        {'name': 'Bell Peppers', 'name_ar': 'فلفل حلو ملون', 'description': 'Colorful bell peppers', 'description_ar': 'فلفل حلو ملون', 'price_range': (2.0, 4.5)},
        {'name': 'Fresh Herbs', 'name_ar': 'أعشاب طازجة', 'description': 'Mixed fresh herbs for cooking', 'description_ar': 'أعشاب طازجة مشكلة للطبخ', 'price_range': (1.0, 4.0)},
        {'name': 'Eggplant', 'name_ar': 'باذنجان طازج', 'description': 'Fresh purple eggplants', 'description_ar': 'باذنجان بنفسجي طازج', 'price_range': (1.8, 4.0)},
    ],
    'grains': [
        {'name': 'Basmati Rice', 'name_ar': 'أرز بسمتي', 'description': 'Premium aged Basmati rice', 'description_ar': 'أرز بسمتي فاخر معتق', 'price_range': (3.0, 8.0)},
        {'name': 'Quinoa', 'name_ar': 'كينوا عضوية', 'description': 'Organic superfood quinoa', 'description_ar': 'كينوا عضوية غذاء فائق', 'price_range': (8.0, 15.0)},
        {'name': 'Whole Wheat', 'name_ar': 'قمح كامل', 'description': 'Organic whole wheat grains', 'description_ar': 'حبوب قمح كاملة عضوية', 'price_range': (2.0, 5.0)},
        {'name': 'Lentils', 'name_ar': 'عدس أحمر', 'description': 'Red lentils rich in protein', 'description_ar': 'عدس أحمر غني بالبروتين', 'price_range': (2.5, 6.0)},
        {'name': 'Chickpeas', 'name_ar': 'حمص مجفف', 'description': 'Dried chickpeas for cooking', 'description_ar': 'حمص مجفف للطبخ', 'price_range': (2.0, 5.5)},
    ],
    'bakery': [
        {'name': 'Arabic Bread', 'name_ar': 'خبز عربي طازج', 'description': 'Fresh traditional Arabic flatbread', 'description_ar': 'خبز عربي تقليدي طازج', 'price_range': (1.0, 3.0)},
        {'name': 'Croissants', 'name_ar': 'كرواسون فرنسي', 'description': 'Buttery French croissants', 'description_ar': 'كرواسون فرنسي بالزبدة', 'price_range': (2.0, 5.0)},
        {'name': 'Whole Grain Bread', 'name_ar': 'خبز الحبوب الكاملة', 'description': 'Healthy whole grain bread', 'description_ar': 'خبز صحي بالحبوب الكاملة', 'price_range': (3.0, 6.0)},
        {'name': 'Pastries', 'name_ar': 'معجنات شرقية', 'description': 'Traditional Middle Eastern pastries', 'description_ar': 'معجنات شرق أوسطية تقليدية', 'price_range': (4.0, 12.0)},
        {'name': 'Cookies', 'name_ar': 'بسكويت محلي الصنع', 'description': 'Homemade cookies with natural ingredients', 'description_ar': 'بسكويت محلي الصنع بمكونات طبيعية', 'price_range': (3.5, 8.0)},
    ],
    'beverages': [
        {'name': 'Arabic Coffee', 'name_ar': 'قهوة عربية أصيلة', 'description': 'Premium Arabic coffee beans', 'description_ar': 'حبوب قهوة عربية فاخرة', 'price_range': (10.0, 25.0)},
        {'name': 'Fresh Juice', 'name_ar': 'عصير طبيعي طازج', 'description': 'Freshly squeezed natural juices', 'description_ar': 'عصائر طبيعية معصورة طازجة', 'price_range': (2.0, 6.0)},
        {'name': 'Herbal Tea', 'name_ar': 'شاي أعشاب', 'description': 'Premium herbal tea blends', 'description_ar': 'خلطات شاي أعشاب فاخرة', 'price_range': (5.0, 15.0)},
        {'name': 'Mineral Water', 'name_ar': 'مياه معدنية', 'description': 'Natural mineral water from springs', 'description_ar': 'مياه معدنية طبيعية من الينابيع', 'price_range': (1.0, 3.0)},
        {'name': 'Energy Drinks', 'name_ar': 'مشروبات الطاقة', 'description': 'Natural energy drinks with vitamins', 'description_ar': 'مشروبات طاقة طبيعية بالفيتامينات', 'price_range': (2.5, 8.0)},
    ],
    'spices': [
        {'name': 'Saffron', 'name_ar': 'زعفران أصلي', 'description': 'Premium saffron threads from Iran', 'description_ar': 'خيوط زعفران فاخرة من إيران', 'price_range': (50.0, 150.0)},
        {'name': 'Cardamom', 'name_ar': 'هيل أخضر', 'description': 'Green cardamom pods', 'description_ar': 'حبات هيل أخضر', 'price_range': (15.0, 30.0)},
        {'name': 'Cinnamon', 'name_ar': 'قرفة سيلانية', 'description': 'Ceylon cinnamon sticks', 'description_ar': 'أعواد قرفة سيلانية', 'price_range': (8.0, 18.0)},
        {'name': 'Black Pepper', 'name_ar': 'فلفل أسود مطحون', 'description': 'Freshly ground black pepper', 'description_ar': 'فلفل أسود مطحون طازج', 'price_range': (5.0, 12.0)},
        {'name': 'Turmeric', 'name_ar': 'كركم طبيعي', 'description': 'Organic turmeric powder', 'description_ar': 'مسحوق كركم عضوي', 'price_range': (3.0, 8.0)},
        {'name': 'Sumac', 'name_ar': 'سماق حامض', 'description': 'Tangy sumac spice', 'description_ar': 'سماق حامض طبيعي', 'price_range': (6.0, 12.0)},
        {'name': 'Za\'atar', 'name_ar': 'زعتر بلدي', 'description': 'Traditional Middle Eastern herb blend', 'description_ar': 'خلطة زعتر شرق أوسطية تقليدية', 'price_range': (4.0, 10.0)},
        {'name': 'Cumin', 'name_ar': 'كمون مطحون', 'description': 'Ground cumin seeds', 'description_ar': 'بذور كمون مطحونة', 'price_range': (4.0, 9.0)},
        {'name': 'Paprika', 'name_ar': 'بابريكا حلوة', 'description': 'Sweet paprika powder', 'description_ar': 'مسحوق بابريكا حلوة', 'price_range': (3.5, 8.0)},
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

def add_products_to_exhibitor(exhibitor, category_products):
    """إضافة منتجات للعارض - Add products to exhibitor"""
    # التحقق من وجود منتجات للعارض
    existing_products_count = Product.query.filter_by(exhibitor_id=exhibitor.id).count()
    
    if existing_products_count > 0:
        print(f"   ⚠️ العارض لديه {existing_products_count} منتج بالفعل - سيتم تخطيه")
        print(f"   ⚠️ Exhibitor already has {existing_products_count} products - skipping")
        return 0
    
    # عدد المنتجات العشوائي - Random number of products
    num_products = random.randint(PRODUCTS_PER_EXHIBITOR_MIN, PRODUCTS_PER_EXHIBITOR_MAX)
    
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
                base_name += f" - Grade {chr(65 + (i % 26))}"  # A, B, C, etc.
            
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
                is_featured=random.choice([True, False]) if random.random() < 0.25 else False,  # 25% chance to be featured
                views_count=random.randint(0, 500),
                inquiries_count=random.randint(0, 50)
            )
            
            db.session.add(product)
            products_added += 1
            
        except Exception as e:
            print(f"❌ خطأ في إضافة المنتج {product_data['name']} للعارض {exhibitor.company_name}: {str(e)}")
            print(f"❌ Error adding product {product_data['name']} to {exhibitor.company_name}: {str(e)}")
            continue
    
    # تحديث عدد المنتجات الكلي للعارض
    if products_added > 0:
        exhibitor.total_products = exhibitor.get_total_products() + products_added
    
    return products_added

def main():
    """الدالة الرئيسية - Main function"""
    with app.app_context():
        print("🚀 بدء إضافة المنتجات للعارضين...")
        print("🚀 Starting to add products to exhibitors...")
        
        # جلب جميع العارضين - Get all exhibitors
        exhibitors = Exhibitor.query.all()
        
        if not exhibitors:
            print("❌ لا توجد عارضين في قاعدة البيانات!")
            print("❌ No exhibitors found in database!")
            return
        
        print(f"📊 تم العثور على {len(exhibitors)} عارض")
        print(f"📊 Found {len(exhibitors)} exhibitors")
        
        total_products_added = 0
        exhibitors_processed = 0
        exhibitors_skipped = 0
        
        for exhibitor in exhibitors:
            print(f"\n🏢 معالجة العارض: {exhibitor.company_name}")
            print(f"🏢 Processing exhibitor: {exhibitor.company_name}")
            
            # تحديد فئة المنتجات بناءً على فئة العارض
            category_key = 'general'  # افتراضي
            
            if exhibitor.category:
                category_name = exhibitor.category.name_en.lower()
                if 'dairy' in category_name or 'milk' in category_name:
                    category_key = 'dairy'
                elif 'meat' in category_name or 'poultry' in category_name:
                    category_key = 'meat'
                elif 'seafood' in category_name or 'fish' in category_name:
                    category_key = 'seafood'
                elif 'fruit' in category_name:
                    category_key = 'fruits'
                elif 'vegetable' in category_name:
                    category_key = 'vegetables'
                elif 'grain' in category_name or 'legume' in category_name:
                    category_key = 'grains'
                elif 'bakery' in category_name or 'bread' in category_name:
                    category_key = 'bakery'
                elif 'beverage' in category_name or 'drink' in category_name:
                    category_key = 'beverages'
                elif 'spice' in category_name:
                    category_key = 'spices'
            
            # إذا لم نجد فئة مناسبة، نختار عشوائياً
            if category_key == 'general':
                category_key = random.choice(list(SAMPLE_PRODUCTS.keys()))
            
            # إضافة المنتجات
            products_added = add_products_to_exhibitor(exhibitor, SAMPLE_PRODUCTS[category_key])
            
            if products_added > 0:
                total_products_added += products_added
                exhibitors_processed += 1
                print(f"   ✅ تم إضافة {products_added} منتج")
                print(f"   ✅ Added {products_added} products")
            else:
                exhibitors_skipped += 1
        
        # حفظ التغييرات
        try:
            db.session.commit()
            print(f"\n🎉 تم الانتهاء بنجاح!")
            print(f"🎉 Successfully completed!")
            print(f"📈 إجمالي المنتجات المضافة: {total_products_added}")
            print(f"📈 Total products added: {total_products_added}")
            print(f"� عدد العارضين المعالجين: {exhibitors_processed}")
            print(f"👥 Exhibitors processed: {exhibitors_processed}")
            print(f"⏭️ عدد العارضين المتخطين: {exhibitors_skipped}")
            print(f"⏭️ Exhibitors skipped: {exhibitors_skipped}")
            if exhibitors_processed > 0:
                print(f"�📊 معدل المنتجات لكل عارض: {total_products_added/exhibitors_processed:.1f}")
                print(f"📊 Average products per exhibitor: {total_products_added/exhibitors_processed:.1f}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ خطأ في حفظ البيانات: {str(e)}")
            print(f"❌ Error saving data: {str(e)}")

if __name__ == "__main__":
    main()
