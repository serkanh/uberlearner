from assessment.models import BooleanQuestion
from main.api import UberModelResource


class QuizResource(UberModelResource):
    class Meta(UberModelResource.Meta):
        resource_name = 'boolean'
        queryset = BooleanQuestion.objects.all()