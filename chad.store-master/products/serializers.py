from rest_framework import serializers
from products.models import Review, Product, Cart, FavoriteProduct, ProductTag


class ProductSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    price = serializers.FloatField()
    currency = serializers.ChoiceField(choices=['GEL', 'USD', 'EUR'])


class ReviewSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(write_only=True)
    content = serializers.CharField()
    rating = serializers.IntegerField()

    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Invalid product_id. Product does not exist.")
        return value

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def create(self, validated_data):
        product = Product.objects.get(id=validated_data['product_id'])
        user = self.context['request'].user

        review = Review.objects.create(
            product=product,
            user=user,
            content=validated_data['content'],
            rating=validated_data['rating'],
        )
        return review
    


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

    def validate_quantity(self, value):
        """რაოდენობა უნდა იყოს 1-ზე მეტი, რადგან 0 ან უარყოფითი მნიშვნელობა არასწორია."""
        if value < 1:
            raise serializers.ValidationError("რაოდენობა უნდა იყოს მინიმუმ 1.")
        return value

    def validate_total_price(self, value):
        """ჯამური ფასი უნდა იყოს 0-ზე მეტი, რადგან უარყოფითი ან ნულოვანი ფასი არასწორია."""
        if value <= 0:
            raise serializers.ValidationError("ჯამური ფასი უნდა იყოს დადებითი რიცხვი.")
        return value


class FavoriteProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteProduct
        fields = '__all__'

    def validate_user(self, value):
        """მომხმარებელი აუცილებელია, რადგან ფავორიტი პროდუქტი მომხმარებელთან არის დაკავშირებული."""
        if not value:
            raise serializers.ValidationError("მომხმარებელი აუცილებელია.")
        return value

    def validate_product(self, value):
        """პროდუქტი აუცილებელია, რადგან ფავორიტების სია პროდუქტის გარეშე არ არსებობს."""
        if not value:
            raise serializers.ValidationError("პროდუქტი აუცილებელია.")
        return value


class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = '__all__'

    def validate_name(self, value):
        """ნიშნის სახელის სიგრძე უნდა იყოს მინიმუმ 4 სიმბოლო, რათა თავიდან ავიცილოთ უაზრო ან ძალიან მოკლე სახელები."""
        if len(value) < 4:
            raise serializers.ValidationError("ნიშნის სახელი უნდა შეიცავდეს მინიმუმ 4 სიმბოლოს.")
        return value

    
