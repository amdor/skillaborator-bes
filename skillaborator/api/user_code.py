from flask_restful import Resource, reqparse
from flask.helpers import make_response
from skillaborator.db_collections import auth_service, one_time_code_service


class UserCode(Resource):
    @staticmethod
    def __parse_args() -> dict:
        parser = reqparse.RequestParser()

        parser.add_argument('email', type=str, required=True, help="Email address of the user")
        parser.add_argument('token', type=str, required=True, help="Access token")

        return parser.parse_args(strict=True)

    @staticmethod
    def get():
        """
        Get one-time code for the authenticated user
        """
        args = UserCode.__parse_args()
        email = args.get("email")
        token = args.get("token")
        can_start_new_eval = auth_service.can_start_new_evaluation(email, token)
        if not can_start_new_eval:
            return "Too early", 403
        new_code = one_time_code_service.find_unused_code(email)
        if new_code is None:
            new_code = one_time_code_service.create_one_time_code(email)
        return make_response({"oneTimeCode": new_code}, 200)
