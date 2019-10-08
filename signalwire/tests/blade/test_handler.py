from unittest import TestCase
from unittest.mock import Mock
from signalwire.blade.handler import register, register_once, unregister, unregister_all, trigger, queue_size, is_queued, clear

class TestBladeMessages(TestCase):
  def setUp(self):
    clear()

  def test_register(self):
    register(event='event_name', callback=lambda x: print(x))
    register(event='event_name', callback=lambda x: print(x))
    register(event='event_name', callback=lambda x: print(x))

    self.assertTrue(is_queued('event_name'))
    self.assertEqual(queue_size('event_name'), 3)

  def test_register_with_unique_id(self):
    register(event='event_name', callback=lambda x: print(x), suffix='xxx')
    register(event='event_name', callback=lambda x: print(x), suffix='yyy')
    register(event='event_name', callback=lambda x: print(x), suffix='zzz')

    self.assertFalse(is_queued('event_name'))
    self.assertEqual(queue_size('event_name', 'xxx'), 1)
    self.assertEqual(queue_size('event_name', 'yyy'), 1)

  def test_register_once(self):
    mock = Mock()
    register_once(event='event_name', callback=mock)
    self.assertEqual(queue_size('event_name'), 1)
    trigger('event_name', 'custom data')
    self.assertEqual(queue_size('event_name'), 0)
    trigger('event_name', 'custom data')
    trigger('event_name', 'custom data')
    mock.assert_called_once()

  def test_register_once_with_unique_id(self):
    mock = Mock()
    register_once(event='event_name', callback=mock, suffix='uuid')
    self.assertEqual(queue_size('event_name', 'uuid'), 1)
    trigger('event_name', 'custom data', suffix='uuid')
    self.assertEqual(queue_size('event_name'), 0)
    trigger('event_name', 'custom data', suffix='uuid')
    trigger('event_name', 'custom data', suffix='uuid')
    mock.assert_called_once()

  def test_unregister(self):
    mock = Mock()
    register(event='event_name', callback=mock)
    self.assertEqual(queue_size('event_name'), 1)

    unregister(event='event_name', callback=mock)
    self.assertEqual(queue_size('event_name'), 0)
    trigger('event_name', 'custom data')
    mock.assert_not_called()

  def test_unregister_with_unique_id(self):
    mock = Mock()
    register(event='event_name', callback=mock, suffix='xxx')
    self.assertEqual(queue_size('event_name', 'xxx'), 1)

    unregister(event='event_name', callback=mock, suffix='xxx')
    self.assertEqual(queue_size('event_name', 'xxx'), 0)
    trigger('event_name', 'custom data', 'xxx')
    mock.assert_not_called()

  def test_unregister_without_callbak(self):
    mock = Mock()
    register(event='event_name', callback=mock)
    self.assertEqual(queue_size('event_name'), 1)

    unregister(event='event_name')
    self.assertEqual(queue_size('event_name'), 0)
    trigger('event_name', 'custom data')
    mock.assert_not_called()

  def test_unregister_all(self):
    mock = Mock()
    register(event='event_name', callback=mock)
    register(event='event_name', callback=mock, suffix='t1')
    register(event='event_name', callback=mock, suffix='t2')
    unregister_all('event_name')
    trigger('event_name', 'custom data')
    trigger('event_name', 'custom data', suffix='t1')
    trigger('event_name', 'custom data', suffix='t2')
    mock.assert_not_called()

  def test_clear(self):
    register(event='event_name', callback=lambda x: print(x))
    self.assertEqual(queue_size('event_name'), 1)
    clear()
    self.assertEqual(queue_size('event_name'), 0)

  def test_trigger(self):
    mock = Mock()
    register(event='event_name', callback=mock)
    mock.assert_not_called()
    trigger('event_name', 'custom data')
    mock.assert_called_once()

  def test_trigger_with_unique_id(self):
    mock1 = Mock()
    register(event='event_name', callback=mock1, suffix='some_uuid')
    mock2 = Mock()
    register(event='event_name', callback=mock2, suffix='other_uuid')
    mock1.assert_not_called()
    mock2.assert_not_called()
    trigger('event_name', 'custom data', suffix='some_uuid')
    mock1.assert_called_once()
    mock2.assert_not_called()
