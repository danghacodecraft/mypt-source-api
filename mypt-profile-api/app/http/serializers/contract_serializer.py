from rest_framework import serializers
from ..models.contract import Contract
from core.helpers import helper
from datetime import datetime


class MyInfoContractSerializer(serializers.ModelSerializer):
    contractCode = serializers.CharField(source="contract_code")
    contractType = serializers.CharField(source="contract_type")
    contractStartDate = serializers.DateField(format="%d/%m/%Y", source="contract_start_date")
    contractEndDate = serializers.DateField(format="%d/%m/%Y", source="contract_end_date")
    recodedType = serializers.SerializerMethodField()

    def to_representation(self, instance):
        data = super(MyInfoContractSerializer, self).to_representation(instance)
        for key, value in data.items():
            if value is None or value == "":
                data[key] = "---"

        return data

    def get_recodedType(self, contract):
        contract_type = contract.contract_type
        contract_end_date = contract.contract_end_date
        if contract_type:
            if contract_type.lower() == "HĐLĐ Không xác định thời hạn".lower() \
                    and contract_end_date is None:
                return "DUE"
            else:
                if contract_end_date and contract_end_date != "":
                    contract_end_date = datetime.strptime(str(contract_end_date), helper.format_date)
                    now_date = datetime.strptime(str(datetime.now().date()),
                                                 helper.format_date)
                    if contract_end_date < now_date:
                        return "EXPIRED"
                    return "DUE"
        return "---"

    class Meta:
        model = Contract
        fields = ["contractCode", "contractType",
                  "contractStartDate", "contractEndDate",
                  "recodedType"]
