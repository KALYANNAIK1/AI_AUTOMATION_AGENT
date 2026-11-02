from datetime import datetime


class NotificationAgent:

    def send_notification(
        self,
        message,
        status="INFO"
    ):

        print("\n====================================")
        print("      AUTOMATION NOTIFICATION         ")
        print("====================================")

        print(
            f"Time   : {datetime.now()}"
        )

        print(
            f"Status : {status}"
        )

        print("\nMessage:")
        print(message)

        print("====================================")

        return {
            "status": "SENT",
            "timestamp": str(
                datetime.now()
            )
        }