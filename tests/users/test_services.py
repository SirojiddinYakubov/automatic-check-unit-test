import pytest
from django.contrib.auth.hashers import make_password

from users.exceptions import OTPException
from users.services import OTPService


def test_otp_service_generate_otp(mocker):
    mock_otp_code = "567483"
    mock_secret_token = "sdNdFhKSt_0p2cbzygxcI9A75doUwSYocr1vTqkjxeM"
    mock_otp_hash = make_password(f"{mock_secret_token}:{mock_otp_code}")
    mock_email = "test@gmail.com"
    expire_in = 120
    check_if_exists = True

    mock_redis_conn = mocker.Mock()
    mocker.patch('users.services.OTPService.get_redis_conn', return_value=mock_redis_conn)
    mock_redis_conn.exists.return_value = None
    mocker.patch('random.choices', return_value=list(mock_otp_code))
    mocker.patch('users.services.token_urlsafe', return_value=mock_secret_token)
    mocker.patch('users.services.make_password', return_value=mock_otp_hash)

    otp_code, secret_token = OTPService.generate_otp(mock_email, expire_in, check_if_exists)
    assert otp_code == mock_otp_code
    assert secret_token == mock_secret_token

    key = f"{mock_email}:otp"
    mock_redis_conn.set.assert_called_once_with(key, mock_otp_hash, ex=expire_in)

    with pytest.raises(OTPException):
        mock_redis_conn.exists.return_value = True
        OTPService.generate_otp(mock_email, expire_in, check_if_exists)
        mock_redis_conn.ttl.assert_called_once_with(key)


def test_otp_service_check_otp(mocker):
    mock_otp_code = "567483"
    mock_secret_token = "sdNdFhKSt_0p2cbzygxcI9A75doUwSYocr1vTqkjxeM"
    mock_email = "test@gmail.com"
    mock_redis_conn = mocker.Mock()
    mocker.patch('users.services.OTPService.get_redis_conn', return_value=mock_redis_conn)
    mock_redis_conn.get.return_value = make_password(f"{mock_secret_token}:{mock_otp_code}").encode()
    key = f"{mock_email}:otp"

    OTPService.check_otp(mock_email, mock_otp_code, mock_secret_token)
    mock_redis_conn.get.assert_called_once_with(key)

    with pytest.raises(OTPException):
        mock_redis_conn.get.return_value = None
        OTPService.check_otp(mock_email, mock_otp_code, mock_secret_token)

    with pytest.raises(OTPException):
        OTPService.check_otp(mock_email, "123456", mock_secret_token)

    with pytest.raises(OTPException):
        OTPService.check_otp(mock_email, mock_otp_code, "fake_secret_token")
