"""pact test for user service client"""
import logging
import sys
import pytest
from pact import Verifier
import os

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class Logger:
    stdout = sys.stdout
    messages = ""

    def start(self):
        sys.stdout = self

    def stop(self):
        sys.stdout = self.stdout

    def write(self, text):
        self.messages += text


# For the purposes of this example, the broker is started up as a fixture defined
# in conftest.py. For normal usage this would be self-hosted or using Pactflow.
PACT_BROKER_URL = os.environ.get("PACT_BROKER_URL")
PACT_BROKER_USERNAME = os.environ.get("PACT_BROKER_USERNAME")
PACT_BROKER_PASSWORD = os.environ.get("PACT_BROKER_PASSWORD")

# !importance input!
CONSUMER_TAG_SELECTOR = os.environ.get("CONSUMER_TAG_SELECTOR")
PROVIDER_VERSION = os.environ.get("PROVIDER_VERSION")
PROVIDER_TAG = os.environ.get("PROVIDER_TAG")


def test_success():
    pass


@pytest.fixture
def broker_opts():
    return {
        "broker_username": PACT_BROKER_USERNAME,
        "broker_password": PACT_BROKER_PASSWORD,
        "broker_url": PACT_BROKER_URL,
        "publish_version": PROVIDER_VERSION,
        "publish_verification_results": True,
        "consumer_tags": [CONSUMER_TAG_SELECTOR],
        "provider_tags": [PROVIDER_TAG]
    }

# For the purposes of this example, the FastAPI provider will be started up as
# a fixture in conftest.py ("server"). Alternatives could be, for example
# running a Docker container with a database of test data configured.
# This is the "real" provider to verify against.
PROVIDER_HOST = "127.0.0.1"

def test_user_service_provider_against_broker(server, broker_opts):
    PROVIDER_PORT = os.getenv("PROVIDER_PORT")
    PROVIDER_URL = f"http://{PROVIDER_HOST}:{PROVIDER_PORT}"
    verifier = Verifier(
        provider="provider-y",
        provider_base_url=PROVIDER_URL
    )

    # Request all Pact(s) from the Pact Broker to verify this Provider against. In the Pact Broker logs,
    # this corresponds to the following entry: PactBroker::Api::Resources::ProviderPactsForVerification -- Fetching
    # pacts for verification by UserService -- {:provider_name=>"UserService", :params=>{}}
    console_log = Logger()
    console_log.start()
    success, logs = verifier.verify_with_broker(
        **broker_opts,
        verbose=False,
        provider_states_setup_url=f"{PROVIDER_URL}/_pact/provider_states",
        enable_pending=False,
    )
    console_log.stop()
    print(console_log.messages)
    # If publish_verification_results is set to True, the results will be
    # published to the Pact Broker.
    # In the Pact Broker logs, this corresponds to the following entry:
    #   PactBroker::Verifications::Service -- Creating verification 200 for \
    #   pact_version_sha=c8568cbb30d2e3933b2df4d6e1248b3d37f3be34 -- \
    #   {"success"=>true, "providerApplicationVersion"=>"3", "wip"=>false, \
    #   "pending"=>"true"}

    # Note:
    #  If "successful", then the return code here will be 0
    #  This can still be 0 and so PASS if a Pact verification FAILS, as long as
    #  it has not resulted in a REGRESSION of an already verified interaction.
    #  See https://docs.pact.io/pact_broker/advanced_topics/pending_pacts/ for
    #  more details.
    assert success == 0
    assert "No pacts were found" not in console_log.messages
