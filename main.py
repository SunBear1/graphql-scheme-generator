import strawberry
from fastapi import FastAPI
from strawberry.asgi import GraphQL

from data_types import Activity, AdditionalParameters, ActivityExecution, Experiment, Participant, ParticipantState, \
    Participation

example_activity = Activity(id=1, name="example_activity",
                            additionalParameters=AdditionalParameters(key="example_key",
                                                                      value="example_value"))

example_activity_execution = ActivityExecution(id=2, name="example_activity_execution", hasActivity=example_activity,
                                               additionalParameters=AdditionalParameters(key="example_key",
                                                                                         value="example_value"))

example_experiment = Experiment(id=3, name="example_experiment", scenario=example_activity_execution,
                                additionalParameters=AdditionalParameters(key="example_key",
                                                                          value="example_value"))

example_participant = Participant(id=4, name="example_participant", additionalParameters=AdditionalParameters(
    key="example_key",
    value="example_value"))

example_participant_state = ParticipantState(id=5, name="example_participant_state",
                                             hasParticipant=example_participant,
                                             additionalParameters=AdditionalParameters(
                                                 key="example_key",
                                                 value="example_value"))

example_participation = Participation(id=6, name="example_participation",
                                      hasActivityExecution=example_activity_execution,
                                      hasParticipantState=example_participant_state,
                                      additionalParameters=AdditionalParameters(key="example_key",
                                                                                value="example_value"))


@strawberry.type
class Query:

    @strawberry.field
    def activity(self) -> Activity:
        return example_activity

    @strawberry.field
    def activity_execution(self) -> ActivityExecution:
        return example_activity_execution

    @strawberry.field
    def experiment(self) -> Experiment:
        return example_experiment

    @strawberry.field
    def participant(self) -> Participant:
        return example_participant

    @strawberry.field
    def participant_state(self) -> ParticipantState:
        return example_participant_state

    @strawberry.field
    def participation(self) -> Participation:
        return example_participation


schema = strawberry.Schema(query=Query)

graphql_app = GraphQL(schema)

app = FastAPI()
app.add_route("/graphql", graphql_app)
app.add_websocket_route("/graphql", graphql_app)
