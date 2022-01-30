import pytest
import os.path

from api import PetFriends
from settings import valid_email, valid_password

pf = PetFriends()


class Tests:

    @pytest.fixture()
    def get_key(self):
        self.pf = PetFriends()
        status, self.key = self.pf.get_api_key(valid_email, valid_password)
        assert status == 200
        assert 'key' in self.key
        return self.key

    def test_get_all_pets_with_valid_key(self, get_key, filter=''):  # filter available values : my_pets
        # Проверяем что запрос всех питомцев возвращает не пустой список
        status, result = self.pf.get_list_of_pets(self.key, filter)
        assert status == 200
        assert len(result['pets']) > 0

    """Следующий тест падает. Причину понять не могу."""
    def test_get_api_key_for_valid_user(self, get_key):
        # Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key
        status, result = self.pf.get_api_key(self.key)
        # Сверяем полученные данные с нашими ожиданиями
        assert status == 200
        assert 'key' in result

    def test_add_new_pet_with_valid_data(self, get_key, name='Oleg', animal_type='CC',
                                         age='2', pet_photo='images/cc.jpg'):
        # Проверяем, можно ли добавить питомца с корректными данными

        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo

        # Отправляем запрос на добавление питомца
        status, result = self.pf.add_new_pet(self.key, name, animal_type, age, pet_photo)

        assert status == 200
        assert result['name'] == name

    def test_successful_delete_self_pet(self, get_key):
        # Проверяем возможность удаления питомца

        # Запрашиваем список своих питомцев
        _, my_pets = pf.get_list_of_pets(self.key, "my_pets")

        # Проверяем - если список своих питомцев пустой,
        # то добавляем нового и опять запрашиваем список своих питомцев
        if len(my_pets['pets']) == 0:
            pf.add_new_pet(self.key, "Zahar", "Bogomol", "3", "images/bog.jpg")
            _, my_pets = pf.get_list_of_pets(self.key, "my_pets")

        # Берём id первого питомца из списка и отправляем запрос на удаление
        pet_id = my_pets['pets'][0]['id']
        status, _ = pf.delete_pet(self.key, pet_id)

        # Ещё раз запрашиваем список своих питомцев
        _, my_pets = pf.get_list_of_pets(self.key, "my_pets")

        # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
        assert status == 200
        assert pet_id not in my_pets.values()

    def test_successful_update_self_pet_info(self, get_key, name='Oleg', animal_type='Iguana', age=3):
        # Проверяем возможность обновления информации о питомце

        # Получаем список своих питомцев
        _, my_pets = pf.get_list_of_pets(self.key, "my_pets")

        # Если список не пустой, то пробуем обновить данные питомца
        if len(my_pets['pets']) > 0:
            status, result = self.pf.update_pet_info(self.key, my_pets['pets'][0]['id'], name, animal_type, age)

            # Проверяем, что статус ответа = 200 и имя питомца соответствует заданному
            assert status == 200
            assert result['name'] == name
        else:
            # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
            raise Exception("There is no my pets")

    def test_get_my_pets_with_valid_key(self, get_key, filter='my_pets'):
        # Проверяем что запрос моих питомцев возвращает не пустой список.
        status, result = self.pf.get_list_of_pets(self.key, filter)
        assert status == 200
        assert len(result['pets']) > 0

    def test_get_all_pets_with_invalid_key(self, get_key, filter=''):
        # Проверяем что запрос всех питомцев с использованием невалидного api ключа возвращает статус 403
        self.key['key'] = self.key['key'] + "1"
        # Делаем валидный ключ невалидным)))

        status, result = self.pf.get_list_of_pets(self.key, filter)
        assert status == 403

    def test_get_api_key_for_invalid_email(self, get_key, email=valid_email, password=valid_password):
        # Проверяем что запрос api ключа с неверным email возвращает статус отличный от 200

        # Меняем email на несуществующий.
        status, result = self.pf.get_api_key(email + "1", password)
        assert status != 200

    def test_get_api_key_for_invalid_password(self, get_key, email=valid_email, password=valid_password):
        # Проверяем что запрос api ключа с неверным password возвращает статус отличный от 200

        # Меняем email на несуществующий.
        status, result = self.pf.get_api_key(email, password + "1")
        assert status != 200

    def test_successful_delete_self_nonexistent_pet(self, get_key):
        # Проверяем возможность удаления несуществующего питомца
        _, my_pets = pf.get_list_of_pets(self.key, "my_pets")

        # Берём id первого питомца из списка, меняем его и отправляем запрос на удаление
        pet_id = my_pets['pets'][0]['id'] + "1"
        status, _ = pf.delete_pet(self.key, pet_id)

        # Проверяем что статус ответа отличен от 200
        assert status != 200

    def test_successful_update_self_nonexistent_pet_info(self, get_key, name='Oleg', animal_type='Iguana', age=7):
        # Проверяем невозможность обновления информации о несуществующем питомце

        # Запрашиваем список своих питомцев
        _, my_pets = pf.get_list_of_pets(self.key, "my_pets")

        # Берём id первого питомца из списка и меняем его
        pet_id = my_pets['pets'][0]['id'] + "1"

        # Отправляем запрос на изменение данных питомца
        status, result = self.pf.update_pet_info(self.key, pet_id, name, animal_type, age)

        # Проверяем, что статус ответа отличен от 200
        assert status != 200

    def test_successful_update_self_pet_info_invalid_key(self, get_key, name='Oleg', animal_type='Iguana', age=7):
        # Проверяем невозможность обновления информации о питомце с использованием невалидного api ключа

        # Запрашиваем список своих питомцев
        _, my_pets = pf.get_list_of_pets(self.key, "my_pets")

        # Делаем валидный ключ невалидным
        self.key['key'] = self.key['key'] + "1"

        # Отправляем запрос на изменение данных первого питомца
        status, result = self.pf.update_pet_info(self.key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем, что статус ответа отличен от 200
        assert status != 200

    def test_successful_delete_self_pet_invalid_key(self, get_key):
        # Проверяем невозможность удаления питомца с использованием невалидного api ключа

        # Запрашиваем список своих питомцев
        _, my_pets = pf.get_list_of_pets(self.key, "my_pets")

        # Делаем валидный ключ невалидным
        self.key['key'] = self.key['key'] + "1"

        # Берём id первого питомца из списка и отправляем запрос на удаление
        pet_id = my_pets['pets'][0]['id'] + "1"
        status, _ = pf.delete_pet(self.key, pet_id)

        # Проверяем, что статус ответа отличен от 200
        assert status != 200

    def test_add_new_pet_with_invalid_data(self, get_key, name='Oleg', animal_type='CC',
                                           age='2', pet_photo='images/cc.pdf'):
        """Проверяем, можно ли добавить питомца с некорректными данными.
        В документации сказано, что файл с фотографией питомца должен быть в формате
        JPG, JPEG или PNG. Мы пытаемся в качестве фотографии отправить файл в формате
        PDF. В итоге питомец всё равно создаётся, а тест, соответственно, падает."""

        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
        # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo

        # Отправляем запрос на добавление питомца
        status, result = self.pf.add_new_pet(self.key, name, animal_type, age, pet_photo)

        # Проверяем, что статус ответа отличен от 200
        assert status != 200