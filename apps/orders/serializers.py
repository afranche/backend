from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'
        # read_only_fields = ('listing', 'field2')  # Add the fields that should be read-only

    # check if listings are empty
    def validate(self, data):
        if not data['listings']:
            raise serializers.ValidationError("You should order at least one product")
        
        # checks that coupons are not used more than once and are not expired
        coupons = data['coupons']
        if len(set(coupons)) != len(coupons):
            raise serializers.ValidationError("You can't use the same coupon twice")
        for coupon in coupons:
            if coupon.is_expired:
                raise serializers.ValidationError("This coupon is expired")

        return data


    '''
     def update(self, instance, validated_data):
        # Control the fields allowed to update on existing orders
        if self.context['request'].user.is_staff:
            pass
            # If the user is staff, allow updating specific fields
            instance.field1 = validated_data.get('field1', instance.field1)
            instance.field2 = validated_data.get('field2', instance.field2)
        return instance

    def create(self, validated_data):
        # Control the fields allowed to update when creating a new order
        if self.context['request'].user.is_staff:
            return Order(**validated_data)
        return Order(field1=validated_data['field1'], field2=validated_data['field2'])  # Adjust 
   
    '''
