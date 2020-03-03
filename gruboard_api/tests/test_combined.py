from pprint import pprint, pformat

from rest_framework.response import Response
from rest_framework import status

from .utils import CombinedTestCase
from gruboard_api.models import Board


class ProperScenario(CombinedTestCase):

    def test_1(self):
        res: Response = self.client.post(
            f"/api/boards/",
            {"title": self.faker.company(),
             "description": self.faker.text(16)}
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        board_id = res.data["created_board"]["id"]
        admin_auth = res.data["created_role"]["auth"]

        res: Response = self.client.post(
            f"/api/boards/{board_id}/roles/?auth={admin_auth}",
            {"title": self.faker.job(),
             "description": self.faker.text(16),
             "type": "editor"}
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        print("Role created!\n", pformat(res.data))
        editor_auth = res.data["auth"]

        res: Response = self.client.get(
            f"/api/boards/{board_id}/?auth={editor_auth}"
        )
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

        for _ in range(10):
            res: Response = self.client.post(
                f"/api/boards/{board_id}/messages/?auth={editor_auth}",
                {"author": self.faker.name(),
                 "content": self.faker.text(32)}
            )
            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            print("Message created!\n", pformat((res.data["id"], res.data["author"])))

        res: Response = self.client.get(
            f"/api/boards/{board_id}/messages/?auth={admin_auth}"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 10)
        print("Message gotten!\n", pformat([(d["id"], d["author"]) for d in res.data]))