from typing import List, Optional

import strawberry

from models.data_types import Activity, \
    AdditionalParameters
from resolvers.resolvers import create_activity, update_activity, \
    delete_activity


@strawberry.input
class AdditionalParameterInput:
    key: str
    value: str


@strawberry.type
class GriseraMutation:

    @strawberry.mutation
    def create_activity(self, name: str,
                        additional_parameters: Optional[List[AdditionalParameterInput]] = None) -> str:
        if additional_parameters is not None:
            additional_params = [AdditionalParameters(key=param["key"], value=param["value"]) for param in
                                 additional_parameters]
        else:
            additional_params = []

        create_activity(Activity(id=1, name=name, additionalParameters=additional_params))
        return "Activity created"

    @strawberry.mutation
    def update_activity(self, _id: str, name: str,
                        additional_parameters: Optional[List[AdditionalParameterInput]] = None) -> str:
        if additional_parameters is not None:
            additional_params = [AdditionalParameters(key=param["key"], value=param["value"]) for param in
                                 additional_parameters]
        else:
            additional_params = []

        update_activity(Activity(id=_id, name=name, additionalParameters=additional_params))
        return "Activity updated"

    @strawberry.mutation
    def delete_activity(self, _id: str) -> str:
        delete_activity(_id=_id)
        return "Activity deleted"
