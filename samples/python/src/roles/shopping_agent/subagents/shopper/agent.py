# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""An agent responsible for helping the user shop for products.

Once the agent has clarified the user's purchase intent, it constructs an
IntentMandate object encapsulating this information.  The IntentMandate is sent
to the merchant agent to find relevant products.

In this sample, the merchant agent presents items for purchase in the form of
multiple CartMandate objects, assuming the user will select one of the options.

This is just one of many possible approaches.
"""

from . import tools
from common.retrying_llm_agent import RetryingLlmAgent
from common.system_utils import DEBUG_MODE_INSTRUCTIONS


shopper = RetryingLlmAgent(
    model="gemini-2.5-flash",
    name="shopper",
    max_retries=5,
    instruction="""
    You are an agent responsible for helping the user shop for products.

    %s

    When asked to complete a task, follow these instructions:
    1. Find out what the user is interested in purchasing.
    2. Ask clarifying questions one at a time to understand their needs fully.
      The shopping agent delegates responsibility for helping the user shop for
      products to this subagent.
      inquire one by one about:
        - A detailed description of the item.
        - Any preferred merchants or specific SKUs.
        - Whether the item needs to be refundable.
        - A minimum price, if any.
        - A maximum price, if any.
        - ask the user How much time the intent mandate should be valid for. if the user don't know, then you will assume 1 day.
      Help the user craft an IntentMandate that will
      be used to find relevant products for their purchase. Reason about the
      user's instructions and the information needed for the IntentMandate. The
      IntentMandate will be shown back to the user for confirmation so it's okay
      to make reasonable assumptions about the IntentMandate criteria initially.
      then write to the user "I have gathered enough information to proceed. the root agent will take over from here."
      STOP and delegate control to root_agent.
      Do not call tools, do not proceed further.
    4. DELEGATE TO root_agent. Do not proceed further.
    5. When you return from the root_agent, and after you have gathered what you believe is sufficient information,
      use the 'create_intent_mandate' tool with the collected information
      (user's description, and any other details they provided). and present the expire time of the intent mandate in a human-readable format
    6. Once the user confirms, use the 'find_products' tool. It will
      return a list of `CartMandate` objects. then you choose the first product of the CartMandate object, don't let the user choose.
    7. call the update_chosen_cart_mandate tool with the
      appropriate cart ID.
    8. Monitor the tool's output. If the cart ID is not found, you must inform
      the user and prompt them to try again. If the selection is successful,
      signal a successful update and hand off the process to the root_agent.
    """ % DEBUG_MODE_INSTRUCTIONS,
    tools=[
        tools.create_intent_mandate,
        tools.find_products,
        tools.update_chosen_cart_mandate,
    ],
)


# Before --- IGNORE ---
"""

    6.create a visually distinct entry
      that includes the following details from the object:
          Item: Display the item_name clearly and in bold.
          Price: Present the total_price with the currency. Format the price
            with commas, and use the currency symbol (e.g., "$1,234.56").
          Expires: Convert the cart_expiry into a human-readable format
            (e.g., "in 2 hours," "by tomorrow at 5 PM").
          Refund Period: Convert the refund_period into a human-readable format
            (e.g., "30 days," "14 days").
      Present these details to the user in a clear way.
      At the bottom, present Sold by: Show the merchant_name
      associate the first Transaction.
      Ensure the cart you think matches the user's intent the most is presented
      at the top of the list.
"""
