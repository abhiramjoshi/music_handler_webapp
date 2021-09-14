from rest_framework import serializers
from . import utils
from .models import Profile

class YTHeadersSerializer(serializers.Serializer):
    cookie = serializers.CharField(empty_value='')
    x_goog_authuser = serializers.CharField()
    x_goog_visitor_id = serializers.CharField()

    def validate_cookie(self, value):
        try:
            utils.verify_cookie(value)
        except Exception as e:
            raise serializers.ValidationError(
                detail= str(e),
                code='invalid' 
            )

    def validate_x_goog_authuser(self, value):
        try:
            utils.verify_x_goog_auth_user()(value)
        except Exception as e:
            raise serializers.ValidationError(
                detail= str(e),
                code='invalid' 
            )

    def validate_x_goog_visitor_id(self, value):
        try:
            utils.verify_x_goog_visitor_id()(value)
        except Exception as e:
            raise serializers.ValidationError(
                detail= str(e),
                code='invalid' 
            )

