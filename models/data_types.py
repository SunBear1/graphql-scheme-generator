from typing import List, Optional

import strawberry


@strawberry.type
class AdditionalParameters:
    """
    A set of additional parameters that can be assigned to any ROAD class.
    """
    key: str
    value: str


@strawberry.type
class Activity:
    """
    A pattern of an activity done within an experiment.
    """
    id: strawberry.ID
    name: str
    additionalParameters: Optional[List[AdditionalParameters]]

@strawberry.type
class ActivityExecution:
    """
    An execution of a specific activity described by an activity pattern. An activity execution takes place in a
    certain period of time.
    """
    id: strawberry.ID
    name: str
    hasActivity: Activity
    additionalParameters: Optional[List[AdditionalParameters]]


@strawberry.type
class Experiment:
    """
    A list of activities done by participants in order to gather various biosignals and emotional states for the
    emotion recognition purpose.
    """
    id: strawberry.ID
    name: str
    scenario: ActivityExecution
    additionalParameters: Optional[List[AdditionalParameters]]


@strawberry.type
class Participant:
    """
    A person taking part in an experiment.
    """
    id: strawberry.ID
    name: str
    additionalParameters: Optional[List[AdditionalParameters]]


@strawberry.type
class ParticipantState:
    """
    A state of a participant at a specific period of time.
    """
    id: strawberry.ID
    name: str
    hasParticipant: Participant
    additionalParameters: Optional[List[AdditionalParameters]]


@strawberry.type
class Participation:
    """
    A participation of a participant within a specific activity execution.
    """
    id: strawberry.ID
    name: str
    hasActivityExecution: ActivityExecution
    hasParticipantState: ParticipantState
    additionalParameters: Optional[List[AdditionalParameters]]
