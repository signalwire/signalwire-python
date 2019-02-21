from unittest import TestCase
import os, pytest
from signalwire.rest import Client as signalwire_client
import vcr

my_vcr = vcr.VCR(
    cassette_library_dir='fixtures/cassettes',
    record_mode='once',
)

@pytest.fixture(scope="module")
def client():
  client = signalwire_client(os.getenv('SIGNALWIRE_ACCOUNT','signalwire-account-123'), os.getenv('SIGNALWIRE_TOKEN', '123456'), signalwire_space_url = os.getenv('SIGNALWIRE_SPACE', 'myaccount.signalwire.com'))
  return client

@my_vcr.use_cassette()
def test_accounts(client):
  account = client.api.accounts(os.getenv('SIGNALWIRE_ACCOUNT','signalwire-account-123')).fetch()
  assert(account.friendly_name == 'LAML testing') 
    

@my_vcr.use_cassette()
def test_applications(client):
  applications = client.applications.list()
  assert(applications[0].sid == '34f49a97-a863-4a11-8fef-bc399c6f0928')

@my_vcr.use_cassette()
def test_local_numbers(client):
  numbers = client.available_phone_numbers("US") \
                .local \
                .list(in_region="WA")
  assert(numbers[0].phone_number == '+12064015921')

@my_vcr.use_cassette()
def test_toll_free_numbers(client):
  numbers = client.available_phone_numbers("US") \
                .toll_free \
                .list(area_code="310")
  assert(numbers[0].phone_number == '+13103590741')

@my_vcr.use_cassette()
def test_conferences(client):
  conferences = client.conferences.list()

  assert(conferences[0].sid == 'a811cb2c-9e5a-415d-a951-701f8e884fb5')

@my_vcr.use_cassette()
def test_conference_members(client):
  participants = client.conferences('a811cb2c-9e5a-415d-a951-701f8e884fb5') \
                     .participants \
                     .list()

  assert(participants[0].call_sid == '7a520324-684d-435c-87c2-ea7975f371d0')

@my_vcr.use_cassette()
def test_incoming_phone_numbers(client):
  incoming_phone_numbers = client.incoming_phone_numbers.list()

  assert(incoming_phone_numbers[0].phone_number == '+18990000001')

@my_vcr.use_cassette()
def test_messages(client):
  message = client.messages.create(
      from_='+15059999999',
      to='+15058888888',
      media_url='https://www.google.com/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png'
  )

  assert(message.sid == 'cbad786b-fdcd-4d2a-bcb2-fff9df045008')

@my_vcr.use_cassette()
def test_media(client):
  media = client.messages('0da01046-5cca-462f-bc50-adae4e1307e1').media.list()
  assert(media[0].sid == 'a1ee4484-99a4-4996-b7df-fd3ceef2e9ec')

@my_vcr.use_cassette()
def test_recordings(client):
  recordings = client.recordings.list()
  assert(recordings[0].call_sid == 'd411976d-d319-4fbd-923c-57c62b6f677a')

@my_vcr.use_cassette()
def test_transcriptions(client):
  transcriptions = client.transcriptions.list()
  assert(transcriptions[0].recording_sid == 'e4c78e17-c0e2-441d-b5dd-39a6dad496f8')

@my_vcr.use_cassette()
def test_queues(client):
  queues = client.queues.list()
  assert(queues[0].sid == '2fd1bc9b-2e1f-41ac-988f-06842700c10d')

@my_vcr.use_cassette()
def test_queue_members(client):
  members = client.queues('2fd1bc9b-2e1f-41ac-988f-06842700c10d').members.list()
  assert(members[0].call_sid == '24c0f807-2663-4080-acef-c0874f45274d')

@my_vcr.use_cassette()
def test_send_fax(client):
  fax = client.fax.faxes.create(
    from_='+15556677888',
    to='+15556677999',
    media_url='https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf'
  )
  assert(fax.sid == 'dd3e1ac4-50c9-4241-933a-5d4e9a2baf31')

@my_vcr.use_cassette()
def test_list_fax(client):
  faxes = client.fax.faxes.list()
  assert(faxes[0].sid == 'dd3e1ac4-50c9-4241-933a-5d4e9a2baf31')

@my_vcr.use_cassette()
def test_fetch_fax(client):
  fax = client.fax.faxes('831455c6-574e-4d8b-b6ee-2418140bf4cd').fetch()
  assert(fax.to == '+15556677999')
  assert(fax.media_url == 'https://s3.us-east-2.amazonaws.com/signalwire-assets/faxes/20190104162834-831455c6-574e-4d8b-b6ee-2418140bf4cd.tiff')

@my_vcr.use_cassette()
def test_fetch_fax_media(client):
  media = client.fax.faxes('831455c6-574e-4d8b-b6ee-2418140bf4cd').media.list()
  assert(media[0].sid == 'aff0684c-3445-49bc-802b-3a0a488139f5')

@my_vcr.use_cassette()
def test_fetch_fax_media_instance(client):
  media = client.fax.faxes('831455c6-574e-4d8b-b6ee-2418140bf4cd').media('aff0684c-3445-49bc-802b-3a0a488139f5').fetch()
  assert(media.url == '/api/laml/2010-04-01/Accounts/signalwire-account-123/Faxes/831455c6-574e-4d8b-b6ee-2418140bf4cd/Media/aff0684c-3445-49bc-802b-3a0a488139f5.json')
