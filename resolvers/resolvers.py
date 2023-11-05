from models.data_types import Activity, AdditionalParameters, ActivityExecution, Participant, Experiment, \
    ParticipantState, \
    Participation


def get_activity_by_id(_id: str) -> Activity:
    # Search for activity with given ID in database
    return Activity(id=1, name="example_activity",
                    additionalParameters=[AdditionalParameters(key="example_key",
                                                               value="example_value")])


def get_activity_by_name(name: str) -> Activity:
    # Search for activity with given name in database
    return Activity(id=2, name=name,
                    additionalParameters=[AdditionalParameters(key="example_key",
                                                               value="example_value")])


def create_activity(activity: Activity) -> Activity:
    # Create activity in database
    ...


def update_activity(activity: Activity) -> Activity:
    # Update activity in database
    ...


def delete_activity(_id: str):
    # Delete activity in database
    ...


##################################################
def get_activity_execution_by_id():
    example_activity = get_activity_by_id()

    return ActivityExecution(id=2, name="example_activity_execution", hasActivity=example_activity,
                             additionalParameters=[AdditionalParameters(key="example_key",
                                                                        value="example_value")])


def get_experiment_by_id():
    example_activity_execution = get_activity_execution_by_id()
    return Experiment(id=3, name="example_experiment", scenario=example_activity_execution,
                      additionalParameters=[AdditionalParameters(key="example_key",
                                                                 value="example_value")])


def get_participant_by_id():
    return Participant(id=4, name="example_participant", additionalParameters=[AdditionalParameters(key="example_key",
                                                                                                    value="example_value")])


def get_participant_state_by_id():
    example_participant = get_participant_by_id()
    return ParticipantState(id=5, name="example_participant_state", hasParticipant=example_participant,
                            additionalParameters=[AdditionalParameters(key="example_key",
                                                                       value="example_value")])


def get_participation_by_id():
    example_participant_state = get_participant_state_by_id()
    example_activity_execution = get_activity_execution_by_id()
    return Participation(id=6, name="example_participation", hasActivityExecution=example_activity_execution,
                         hasParticipantState=example_participant_state,
                         additionalParameters=[AdditionalParameters(key="example_key",
                                                                    value="example_value")])
