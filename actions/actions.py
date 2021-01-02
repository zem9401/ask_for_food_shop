# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from typing import Dict, Text, Any, List, Union
from rasa_sdk.events import UserUtteranceReverted, Restarted
from rasa_sdk import Tracker, Action
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction
from actions import ChatApis
from actions.ChatApis import get_weather_by_day
from actions.ChatApis import food_poi
from requests import (
    ConnectionError,
    HTTPError,
    TooManyRedirects,
    Timeout
)


class FoodForm(FormAction):

    # 创建表单
    def name(self) -> Text:
        return "food_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["address", "food_shop"]

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        address = tracker.get_slot('address')
        food_shop = tracker.get_slot('food_shop')

        food_shop_list = get_food_shop(address)[address]
        food_shop_str = ''
        for i in food_shop_list:
            food_shop_str = food_shop_str + i + ', '
        dispatcher.utter_message("%s 的附近有以下几个美食小店：%s" % (address, food_shop_str))
        return [Restarted()]

def get_text_weather_date(address, date_time, date_time_number):
    try:
        result = get_weather_by_day(address, date_time_number)
    except (ConnectionError, HTTPError, TooManyRedirects, Timeout) as e:
        text_message = "{}".format(e)
    else:
        text_message_tpl = "{} {} ({}) 的天气情况为: 白天 {}, 夜晚 {},气温:{}-{} 度"

        text_message = text_message_tpl.format(
            result['location']['name'],
            date_time,
            result['result']['date'],
            result['result']['text_day'],
            result['result']['text_night'],
            result['result']["high"],
            result['result']["low"],
        )

    return text_message


def get_food_shop(address):
    food_poi("", address)

# action_default_fallback
class ActionDefaultFallback(Action):
    def name(self):
        return 'action_default_fallback'

    def run(self, dispatcher, tracker, domain):

        # 访问图灵机器人API(闲聊)
        text = tracker.latest_message.get('text')
        message = ChatApis.get_response(text)
        if message is not None:
            dispatcher.utter_message(message)
        else:
            dispatcher.utter_template('utter_default', tracker, silent_fail=True)
        return [UserUtteranceReverted()]