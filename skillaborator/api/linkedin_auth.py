from skillaborator.db_collections.one_time_code_service import one_time_code_service
from flask.helpers import make_response
from skillaborator.db_collections.auth_service import auth_service
from requests import post, get
from flask_restful import Resource, reqparse


class LinkedInAuth(Resource):
    @staticmethod
    def __parse_post_args():
        # TODO: reusable parser?
        parser = reqparse.RequestParser()

        parser.add_argument('client_id', type=str, required=True, location="form")
        parser.add_argument('code', type=str, required=True, location="form")
        parser.add_argument('grant_type', type=str, required=True, location="form")
        parser.add_argument('client_secret', type=str, required=True, location="form")
        parser.add_argument('redirect_uri', type=str, required=True, location="form")

        return parser.parse_args(strict=True)

    @staticmethod
    def __parse_get_args() -> dict:
        parser = reqparse.RequestParser()

        parser.add_argument('email', type=str, required=True, help="Email address of the user")
        parser.add_argument('token', type=str, required=True, help="Access token")

        return parser.parse_args(strict=True)

    @staticmethod
    def post():
        """
        Get access token
        """
        args = LinkedInAuth.__parse_post_args()
        args['redirect_uri'] = "http://localhost:4200"
        resp = post(url="https://www.linkedin.com/oauth/v2/accessToken", params=args, headers={"Content-Type": "x-www-form-urlencoded"})
        token = resp.json()['access_token']
        get_resp = get("https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))", headers={"Authorization": f"Bearer {token}"})
        email = get_resp.json()["elements"][0]["handle~"]["emailAddress"]
        auth_service.save_login(email, token)
        return make_response({"email": email, "token": token}, 200)

    @staticmethod
    def get():
        """
        Get one-time code for the authenticated user
        """
        args = LinkedInAuth.__parse_get_args()
        email = args.get("email")
        token = args.get("token")
        can_start_new_eval = auth_service.can_start_new_evaluation(email, token)
        if not can_start_new_eval:
            return "Too early", 403
        new_code = one_time_code_service.find_unused_code(email)
        if new_code is None:
            new_code = one_time_code_service.create_one_time_code(email)
        return make_response({"oneTimeCode": new_code}, 200)

        
    
