import xml.dom.minidom
from xml.parsers.expat import ExpatError
import lxml.etree as etree


class DictToXml:
    """
    Класс для преобразования словаря в XML c бизнес данными.
    Т.к сложность вставки в словарь O(1) поэтому принято решение
    сделать формирование XML через словарь.

    Преобразование может осуществляться с помощью :: если необходимо сделать так чтобы было
    несколько тегов с одинаковыми именами.
    Например:

    Словарь:

    basic_dict_test = {}
    basic_dict_test["resource"] = {}
    basic_dict_test["resource"]["Organization::1"] = {}
    basic_dict_test["resource"]["Organization::2"] = {}

    Результат:

    <resource>
        <Organization/>
        <Organization/>
    </resource>

    Если передаем ключ c помощью @, то формируем как атрибут.
    Если передается словарь, то формируем закрывающийся тег.
    Например, input:
    mydict = {
            'children': {'children_two': {'@value': 'Tom3'}},
    }
    Output:
    <children><children_two value="Tom3"/></children>
    """

    def __init__(self, name_wrapper=None, name_space=None):
        self.name_wrapper = name_wrapper if name_wrapper else 'WRAPPER_NOT_FOUND'
        self.name_space = name_space if name_space else ''

    def __check_if_dublicate_tag(self, tag_value):
        """Функция для проверки дубликата, может быть несколько тегов."""
        if tag_value and '::' in tag_value:
            value, _ = tag_value.split('::')
            result = value
        else:
            result = tag_value

        return result

    def __dict2xml(self, dict_data, root_node=None):
        """
        Функция для конверта словаря в XML.
        Если передаем ключ c помощью @, то формируем как атрибут.
        Если передается словарь, то формируем закрывающийся тег.
        Например, input:
        mydict = {
            'children': {'children_two': {'@value': 'Tom3'}},
        }
        Output:
        <children><children_two value="Tom3"/></children>
        """
        wrap = False if root_node is None or isinstance(dict_data, list) else True
        root = None if root_node is None else root_node

        root_singular = root[:-1] if root_node and 's' == root[-1] is None else root
        root_singular = self.__check_if_dublicate_tag(root_singular)
        xml = ''
        children = []

        if isinstance(dict_data, dict):
            for key, value in dict.items(dict_data):
                if isinstance(value, dict):
                    key = self.__check_if_dublicate_tag(key)
                    children.append(self.__dict2xml(value, key))
                elif isinstance(value, list):
                    children.append(self.__dict2xml(value, key))
                # Используется когда необходимо сформировать значение атрибута
                elif '@' in key:
                    value_key = key.replace('@', '')
                    xml = f'{xml} {value_key}="{value}"'
                # Используется когда необходимо сформировать данные внутри
                # закрывающегося тега
                elif '#' in value:
                    number_tag, value_into_tag = value.split(':::')
                    xml = f'{xml} <{key}>{value_into_tag}</{key}>'
        else:
            for value in dict_data:
                children.append(self.__dict2xml(value, root_singular))

        end_tag = '>' if 0 < len(children) else '/>'

        if wrap or isinstance(dict_data, dict) and root is not None:
            xml = f'<{root}{xml}{end_tag}'

        if 0 < len(children):
            for child in children:
                xml = f'{xml}{child}'

            if wrap or isinstance(dict_data, dict) and root is not None:
                xml = f'{xml}</{root}>'

        return xml

    def xml_build_from_dict(self, dict_data):
        """Для того чтобы создать с именем пространств и тегом бизнес данных."""
        xml_result = self.__dict2xml(dict_data)
        xml_result = f'<{self.name_wrapper}{self.name_space}>{xml_result}</{self.name_wrapper}>'

        try:
            dom = xml.dom.minidom.parseString(xml_result)
            pretty_xml_as_string = dom.toprettyxml()
            # Сделали константу NAMESPACE т.к xml.dom.minidom.parseString(xml_string) не может
            # распарсить двоеточие
            pretty_xml_as_string = pretty_xml_as_string.replace('NAMESPACE', ':')
            pretty_xml_as_string = pretty_xml_as_string.replace('<?xml version="1.0" ?>', '')
        except ExpatError:
            with open('except_xml.xml', mode='w+') as file:
                file.write(xml_result)

            x = etree.parse('except_xml.xml')
            etree.tostring(x, pretty_print=True)

        # Либа, которая парсит XML для задания отступов и табуляций
        # просит чтобы был единый врапер, поэтому по умолчанию ставим это значений
        if 'WRAPPER_NOT_FOUND' in pretty_xml_as_string:
            pretty_xml_as_string = pretty_xml_as_string.replace('<WRAPPER_NOT_FOUND>', '')
            pretty_xml_as_string = pretty_xml_as_string.replace('</WRAPPER_NOT_FOUND>', '')

        return pretty_xml_as_string

