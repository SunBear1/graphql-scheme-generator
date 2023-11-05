import strawberry

from data_types import ActivityExecution, Experiment, Participant, ParticipantState, Participation, Activity
from resolvers import get_participant_by_id, get_participant_state_by_id, get_participation_by_id, get_activity_by_id, \
    get_activity_execution_by_id, get_experiment_by_id, get_activity_by_name


@strawberry.type
class GriseraQuery:

    @strawberry.field
    def activity_by_id(self, _id: str) -> Activity:
        return get_activity_by_id(_id=_id)

    @strawberry.field
    def activity_by_name(self, name: str) -> Activity:
        return get_activity_by_name(name=name)

    @strawberry.field
    def activity_execution(self) -> ActivityExecution:
        return get_activity_execution_by_id()

    @strawberry.field
    def experiment(self) -> Experiment:
        return get_experiment_by_id()

    @strawberry.field
    def participant(self) -> Participant:
        return get_participant_by_id()

    @strawberry.field
    def participant_state(self) -> ParticipantState:
        return get_participant_state_by_id()

    @strawberry.field
    def participation(self) -> Participation:
        return get_participation_by_id()
