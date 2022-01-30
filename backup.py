import pytest
import os.path

from api import PetFriends
from settings import valid_email, valid_password

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""
    status, result = pf.get_api_key(email, password)
    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
        Для этого сначала получаем api ключ и сохраняем в переменную auth_key.
        Далее используя этот ключ запрашиваем список всех питомцев и проверяем что список не пустой."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Запрашиваем ключ api и сохраняем в переменную auth_key

    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Oleg', animal_type='CC',
                                     age='2', pet_photo='images/cc.jpg'):
    """Проверяем, можно ли добавить питомца с корректными данными"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Запрашиваем ключ api и сохраняем в переменную auth_key

    # Отправляем запрос на добавление питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    # Проверяем возможность удаления питомца

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой,
    # то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Zahar", "Bogomol", "3", "images/bog.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Oleg', animal_type='Iguana', age=3):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить данные питомца
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


def test_get_my_pets_with_valid_key(filter='my_pets'):
    """Проверяем что запрос моих питомцев возвращает не пустой список.
        Для этого сначала получаем api ключ и сохраняем в переменную auth_key.
        Далее используя этот ключ запрашиваем список моих питомцев и проверяем что список не пустой."""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Запрашиваем ключ api и сохраняем в переменную auth_key

    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_get_all_pets_with_invalid_key(filter=''):
    """ Проверяем что запрос всех питомцев с использованием невалидного api ключа возвращает статус 403.
        Для этого сначала получаем api ключ и сохраняем в переменную auth_key.
        Далее изменяем переменную auth_key и выполняем запрос"""

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Запрашиваем ключ api и сохраняем в переменную auth_key

    auth_key['key'] = auth_key['key'] + "1"
    # Делаем валидный ключ невалидным)))

    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 403


def test_get_api_key_for_invalid_email(email=valid_email, password=valid_password):
    """Проверяем что запрос api ключа с неверным email возвращает статус отличный от 200"""

    # Меняем email на несуществующий.
    status, result = pf.get_api_key(email + "1", password)
    assert status != 200


def test_get_api_key_for_invalid_password(email=valid_email, password=valid_password):
    """Проверяем что запрос api ключа с неверным password возвращает статус отличный от 200"""

    # Меняем email на несуществующий.
    status, result = pf.get_api_key(email, password + "1")
    assert status != 200


def test_successful_delete_self_nonexistent_pet():
    # Проверяем возможность удаления несуществующего питомца

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка, меняем его и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id'] + "1"
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Проверяем что статус ответа отличен от 200
    assert status != 200


def test_successful_update_self_nonexistent_pet_info(name='Oleg', animal_type='Iguana', age=7):
    """Проверяем невозможность обновления информации о несуществующем питомце"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и меняем его
    pet_id = my_pets['pets'][0]['id'] + "1"

    # Отправляем запрос на изменение данных питомца
    status, result = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)

    # Проверяем, что статус ответа отличен от 200
    assert status != 200


def test_successful_update_self_pet_info_invalid_key(name='Oleg', animal_type='Iguana', age=7):
    """ Проверяем невозможность обновления информации о питомце с использованием
    невалидного api ключа"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Делаем валидный ключ невалидным
    auth_key['key'] = auth_key['key'] + "1"

    # Отправляем запрос на изменение данных первого питомца
    status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

    # Проверяем, что статус ответа отличен от 200
    assert status != 200


def test_successful_delete_self_pet_invalid_key():
    # Проверяем невозможность удаления питомца с использованием невалидного api ключа

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Делаем валидный ключ невалидным
    auth_key['key'] = auth_key['key'] + "1"

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id'] + "1"
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Проверяем, что статус ответа отличен от 200
    assert status != 200


def test_add_new_pet_with_invalid_data(name='Oleg', animal_type='CC',
                                       age='2', pet_photo='images/cc.pdf'):
    """Проверяем, можно ли добавить питомца с некорректными данными.
    В документации сказано, что файл с фотографией питомца должен быть в формате
    JPG, JPEG или PNG. Мы пытаемся в качестве фотографии отправить файл в формате
    PDF. В итоге питомец всё равно создаётся, а тест, соответственно, падает."""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    # Запрашиваем ключ api и сохраняем в переменную auth_key

    # Отправляем запрос на добавление питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Проверяем, что статус ответа отличен от 200
    assert status != 200