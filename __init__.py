from flask import Blueprint

from CTFd.models import Challenges, Flags, db
from CTFd.plugins import challenges, register_plugin_assets_directory
from CTFd.plugins.flags import get_flag_class
from CTFd.plugins.migrations import upgrade
from CTFd.utils.uploads import delete_file


class MultipleChoice(Challenges):
    __tablename__ = "multiple_choice"
    __mapper_args__ = {"polymorphic_identity": "multiple_choice"}
    id = db.Column(
        db.Integer, db.ForeignKey("challenges.id", ondelete="CASCADE"), primary_key=True
    )

    def __init__(self, *args, **kwargs):
        super(MultipleChoice, self).__init__(**kwargs)


class MultipleChoiceChallenge(challenges.BaseChallenge):
    __version__ = "1.1.2"
    id = "multiple_choice"  # Unique identifier used to register challenges
    name = "multiple_choice"  # Name of a challenge type
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        "create": "/plugins/multiple_choice/assets/create.html",
        "update": "/plugins/multiple_choice/assets/update.html",
        "view": "/plugins/multiple_choice/assets/view.html",
    }
    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/multiple_choice/assets/create.js",
        "update": "/plugins/multiple_choice/assets/update.js",
        "view": "/plugins/multiple_choice/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/multiple_choice/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "multiple_choice", __name__, template_folder="templates", static_folder="assets"
    )
    challenge_model = MultipleChoice

    @staticmethod
    def attempt(chal, request):
        """
        This method is used to check whether a given input is right or wrong. It does not make any changes and should
        return a boolean for correctness and a string to be shown to the user. It is also in charge of parsing the
        user's input from the request itself.

        :param chal: The Challenge object from the database
        :param request: The request the user submitted
        :return: (boolean, string)
        """
        data = request.form or request.get_json()
        submission = data.get("submission")
        if submission:
            submission = submission.strip()
        else:
            return False, "Please select a choice"
        chal_keys = Flags.query.filter_by(challenge_id=chal.id).all()
        for chal_key in chal_keys:
            if get_flag_class(chal_key.type).compare(chal_key, submission):
                return True, "Correct"
        return False, "Incorrect"


def load(app):
    upgrade()
    challenges.CHALLENGE_CLASSES["multiple_choice"] = MultipleChoiceChallenge
    register_plugin_assets_directory(app, base_path="/plugins/multiple_choice/assets/")
