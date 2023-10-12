from rest_framework import serializers
from ...core.helpers import my_datetime


class SalaryDailyValidate(serializers.Serializer):
    dateFrom = serializers.DateField(
        error_messages={
            'invalid': 'dateFrom không hợp lệ (format: YYYY-MM-DD)',
            'null': 'dateFrom không là giá trị null!'
        })
    dateTo = serializers.DateField(
        error_messages={
            'invalid': 'dateTo không hợp lệ (format: YYYY-MM-DD)',
            'null': 'dateTo không là giá trị null!'
        })

    def validate(self, data):
        date_from = data["dateFrom"]
        date_to = data["dateTo"]

        if date_to < date_from:
            raise serializers.ValidationError("dateTo không nhỏ hơn dateFrom!")

        if not date_to.year == date_from.year:
            raise serializers.ValidationError("dateTo phải cùng năm với dateFrom!")

        if not date_to.month == date_from.month:
            raise serializers.ValidationError("dateTo phải cùng tháng với dateFrom!")

        return data


class SalaryMonthlyValidate(serializers.Serializer):
    dateFrom = serializers.CharField(
        required=True,
        error_messages={
            'blank': 'dateFrom không hợp lệ (format: YYYY-MM)',
            'null': 'dateFrom không hợp lệ (format: YYYY-MM)',
            'required': 'dateFrom là bắt buộc!'
        })
    dateTo = serializers.CharField(
        required=True,
        error_messages={
            'blank': 'dateTo không hợp lệ (format: YYYY-MM)',
            'null': 'dateTo không hợp lệ (format: YYYY-MM)',
            'required': 'dateTo là bắt buộc!'
        })

    def validate_dateFrom(self, date_from):
        date_from = f"{date_from}-01"
        if not my_datetime.checkDateFormat(date_from, "%Y-%m-%d"):
            raise serializers.ValidationError("dateFrom không hợp lệ (format: YYYY-MM)")
        return date_from

    def validate_dateTo(self, date_to):
        date_to = f"{date_to}-01"
        if not my_datetime.checkDateFormat(date_to, "%Y-%m-%d"):
            raise serializers.ValidationError("dateTo không hợp lệ (format: YYYY-MM)")
        return date_to

    def validate(self, data):
        date_from = my_datetime.strToDate(data["dateFrom"], "%Y-%m-%d").date()
        date_to = my_datetime.strToDate(data["dateTo"], "%Y-%m-%d").date()

        if date_to < date_from:
            raise serializers.ValidationError("dateTo không nhỏ hơn dateFrom!")

        if not date_to.year == date_from.year:
            raise serializers.ValidationError("dateTo phải cùng năm với dateFrom!")

        return data
