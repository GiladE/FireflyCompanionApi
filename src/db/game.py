from ulid import ULID
from enum import Enum
from pynamodb.attributes import UnicodeAttribute
from pynamodb_attributes import UnicodeEnumAttribute
from .base import Base


class GameStates(Enum):
    WAITING_ROOM = "WAITING_ROOM"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    DELETED = "DELETED"


class GameStateError(Exception):
    def __init__(self, current_state, expected_state, action):
        self.current_state = current_state
        self.expected_state = expected_state
        self.action = action
        super().__init__(self._generate_message())

    def _generate_message(self):
        return (
            f"GameStateError: Cannot {self.action} when the game state is '{self.current_state}'. "
            f"Expected state: '{self.expected_state}'."
        )


# PK = GAME::<game_id:str>
# SK = GAME::<game_id:str>

# GSI1PK = GAME_CODE::<game_code:str>
# GSI1SK = GAME_CODE::<game_code:str>


class Game(Base, discriminator="game"):
    game_id = UnicodeAttribute()
    game_code = UnicodeAttribute()
    state = UnicodeEnumAttribute(GameStates, default=GameStates.WAITING_ROOM)

    @classmethod
    def find(cls, game_id):
        try:
            return cls.query(
                f"GAME::{game_id}",
                cls.SK == f"GAME::{game_id}",
                limit=1,
            ).next()
        except StopIteration as exc:
            raise Game.DoesNotExist() from exc

    @classmethod
    def find_or_create(cls, game_code, **args):
        try:
            return cls.find_by_game_code(game_code)
        except Game.DoesNotExist:
            pass

        game_id = ULID()
        return cls(
            f"GAME::{game_id}",
            f"GAME::{game_id}",
            GSI1PK=f"GAME_CODE::{game_code}",
            GSI1SK=f"GAME_CODE::{game_code}",
            game_id=game_id,
            game_code=game_code,
            **args,
        ).save()

    @classmethod
    def find_by_game_code(self, game_code):
        try:
            return self.gsi1.query(
                f"GAME_CODE::{game_code}",
                self.GSI1SK == f"GAME_CODE::{game_code}",
                limit=1,
            ).next()
        except StopIteration as exc:
            raise Game.DoesNotExist() from exc

    def resume_game(self):
        self._update_state(
            GameStates.INACTIVE,
            GameStates.ACTIVE,
            "resume the game",
        )

    def pause_game(self):
        self._update_state(
            GameStates.ACTIVE,
            GameStates.INACTIVE,
            "pause the game",
        )

    def start_game(self):
        self._update_state(
            GameStates.WAITING_ROOM,
            GameStates.ACTIVE,
            "start the game",
        )

    def end_game(self):
        self._clear_indices()
        self._update_state(
            GameStates.ACTIVE,
            GameStates.INACTIVE,
            "end the game",
        )

    def _update_state(self, expected_state, new_state, action):
        if self.state.value != expected_state:
            raise GameStateError(
                current_state=self.state.value,
                expected_state=expected_state.value,
                action=action,
            )
        self.state = new_state
        self.save()

    def _clear_indices(self):
        self.GSI1PK = None
        self.GSI1SK = None
