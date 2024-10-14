import datetime
from ulid import ULID
from pynamodb.indexes import AllProjection, GlobalSecondaryIndex
from pynamodb.models import Model
from pynamodb.attributes import (
    DiscriminatorAttribute,
    UTCDateTimeAttribute,
    UnicodeAttribute,
)


class GSI1(GlobalSecondaryIndex):
    GSI1PK = UnicodeAttribute(hash_key=True)
    GSI1SK = UnicodeAttribute(range_key=True)

    class Meta:
        index_name = "GSI1"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()


class GSI2(GlobalSecondaryIndex):
    GSI2PK = UnicodeAttribute(hash_key=True)
    GSI2SK = UnicodeAttribute(range_key=True)

    class Meta:
        index_name = "GSI2"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()


class GSI3(GlobalSecondaryIndex):
    GSI3PK = UnicodeAttribute(hash_key=True)
    GSI3SK = UnicodeAttribute(range_key=True)

    class Meta:
        index_name = "GSI3"
        billing_mode = "PAY_PER_REQUEST"
        projection = AllProjection()


class Base(Model):
    kind = DiscriminatorAttribute()

    PK = UnicodeAttribute(hash_key=True)
    SK = UnicodeAttribute(range_key=True)

    gsi1 = GSI1()
    GSI1PK = UnicodeAttribute(null=True)
    GSI1SK = UnicodeAttribute(null=True)

    gsi2 = GSI2()
    GSI2PK = UnicodeAttribute(null=True)
    GSI2SK = UnicodeAttribute(null=True)

    gsi3 = GSI3()
    GSI3PK = UnicodeAttribute(null=True)
    GSI3SK = UnicodeAttribute(null=True)

    created_at = UTCDateTimeAttribute(
        default=lambda: datetime.datetime.now(datetime.timezone.utc)
    )

    def set_gsi_1(self, pk, sk):
        self.GSI1PK = pk
        self.GSI1SK = sk

    def set_gsi_2(self, pk, sk):
        self.GSI2PK = pk
        self.GSI2SK = sk

    def set_gsi_3(self, pk, sk):
        self.GSI3PK = pk
        self.GSI3SK = sk

    class Meta:
        table_name = "FireflyCompanionApi-db"
        billing_mode = "PAY_PER_REQUEST"
        region = "eu-west-1"


def ulid():
    return str(ULID())
