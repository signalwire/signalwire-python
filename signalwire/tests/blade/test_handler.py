from unittest import TestCase
from unittest.mock import Mock
from signalwire.blade.handler import register, register_once, unregister, trigger, queue_size, is_queued, clear

class TestBladeMessages(TestCase):
  def setUp(self):
    clear()

  def test_register(self):
    register('event_name', lambda x: print(x))
    register('event_name', lambda x: print(x))
    register('event_name', lambda x: print(x))

    self.assertTrue(is_queued('event_name'))
    self.assertEqual(queue_size('event_name'), 3)

  def test_register_with_unique_id(self):
    register('event_name', lambda x: print(x), 'xxx')
    register('event_name', lambda x: print(x), 'yyy')
    register('event_name', lambda x: print(x), 'zzz')

    self.assertFalse(is_queued('event_name'))
    self.assertEqual(queue_size('event_name', 'xxx'), 1)
    self.assertEqual(queue_size('event_name', 'yyy'), 1)

  def test_register_once(self):
    mock = Mock()
    register_once('event_name', mock)
    self.assertEqual(queue_size('event_name'), 1)
    trigger('event_name', 'custom data')
    self.assertEqual(queue_size('event_name'), 0)
    trigger('event_name', 'custom data')
    trigger('event_name', 'custom data')
    mock.assert_called_once()

  def test_register_once_with_unique_id(self):
    mock = Mock()
    register_once('event_name', mock, 'uuid')
    self.assertEqual(queue_size('event_name', 'uuid'), 1)
    trigger('event_name', 'custom data', 'uuid')
    self.assertEqual(queue_size('event_name'), 0)
    trigger('event_name', 'custom data', 'uuid')
    trigger('event_name', 'custom data', 'uuid')
    mock.assert_called_once()

  def test_unregister(self):
    mock = Mock()
    register('event_name', mock)
    self.assertEqual(queue_size('event_name'), 1)

    unregister('event_name', mock)
    self.assertEqual(queue_size('event_name'), 0)
    trigger('event_name', 'custom data')
    mock.assert_not_called()

  def test_unregister_with_unique_id(self):
    mock = Mock()
    register('event_name', mock, 'xxx')
    self.assertEqual(queue_size('event_name', 'xxx'), 1)

    unregister('event_name', mock, 'xxx')
    self.assertEqual(queue_size('event_name', 'xxx'), 0)
    trigger('event_name', 'custom data', 'xxx')
    mock.assert_not_called()

  def test_unregister_without_callbak(self):
    mock = Mock()
    register('event_name', mock)
    self.assertEqual(queue_size('event_name'), 1)

    unregister('event_name', None)
    self.assertEqual(queue_size('event_name'), 0)
    trigger('event_name', 'custom data')
    mock.assert_not_called()

  def test_clear(self):
    register('event_name', lambda x: print(x))
    self.assertEqual(queue_size('event_name'), 1)
    clear()
    self.assertEqual(queue_size('event_name'), 0)

  def test_trigger(self):
    mock = Mock()
    register('event_name', mock)
    mock.assert_not_called()
    trigger('event_name', 'custom data')
    mock.assert_called_once()

  def test_trigger_with_unique_id(self):
    mock1 = Mock()
    register('event_name', mock1, 'some_uuid')
    mock2 = Mock()
    register('event_name', mock2, 'other_uuid')
    mock1.assert_not_called()
    mock2.assert_not_called()
    trigger('event_name', 'custom data', 'some_uuid')
    mock1.assert_called_once()
    mock2.assert_not_called()
