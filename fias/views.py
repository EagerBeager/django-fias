#coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.utils.text import force_unicode

from django_select2.views import Select2View, NO_ERR_RESP

from fias.models import AddrObj, SocrBase

EMPTY_RESULT = NO_ERR_RESP, False, ()


class SuggestAddressView(Select2View):

    def get_results(self, request, term, page, context):
        filter_params = None

        level = 0
        result_parts = []
        result = []
        parts = term.split(',')

        parts_len = len(parts)

        """
            Проверяем иерархию для всех объектов перед последней запятой
        """
        if parts_len > 1:


            for part in parts[:-1]:
                socr_term, obj_term = part.strip().split(' ', 1)
                socr_term = socr_term.rstrip('.')
                part_qs = AddrObj.objects.filter(shortname__iexact=socr_term, formalname__iexact=obj_term)

                if level > 0:
                    part_qs = part_qs.filter(parentguid=result_parts[level-1].aoguid)

                if len(part_qs) == 1:
                    level += 1
                    result_parts.append(part_qs[0])
                elif len(part_qs) > 1:
                    raise Exception('Много вариантов???')
                else:
                    raise Exception('Empty')
                    return EMPTY_RESULT

        """
            Строку после последней запятой проверяем более тщательно
        """

        last = parts[-1].lstrip()
        last_len = len(last)

        # Это сокращение и начало названия объекта?
        if ' ' in last:
            socr_term, obj_term = last.split(' ', 1)
            socr_term = socr_term.rstrip('.')

            sqs = SocrBase.objects.filter(scname__istartswith=socr_term).distinct()

            if level > 0:
                sqs = sqs.filter(level__gt=result_parts[-1].aolevel)

            sqs_len = len(sqs)
            obj_term = obj_term.strip()

            if sqs_len > 1:
                levels = []
                socrs = []
                for s in sqs:
                    levels.append(s.level)
                    socrs.append(s.scname)

                filter_params = dict(
                    aolevel__in=set(levels),
                    shortname__in=set(socrs),
                )
            elif sqs_len == 1:
                filter_params = dict(
                    aolevel=sqs[0].level,
                    shortname=sqs[0].scname,
                )
            else:
                pass

            if filter_params:
                if obj_term:
                    filter_params.update(formalname__istartswith=obj_term)
                if level > 0:
                    filter_params.update(parentguid=result_parts[-1].aoguid, aolevel__gt=result_parts[-1].aolevel)

        # Это только сокращение?
        elif last_len < 10:
            sqs = SocrBase.objects.filter(scname__istartswith=last)

            if level > 0:
                sqs = sqs.filter(level__gt=result_parts[-1].aolevel)

            sqs_len = len(sqs)
            if sqs_len:
                result = ((None, s.scname) for s in sqs)
            else:
                filter_params = dict(
                    formalname__istartswith=last
                )

                if level > 0:
                    filter_params.update(parentguid=result_parts[-1].aoguid, aolevel__gt=result_parts[-1].aolevel)

        prefix = ', '.join((force_unicode(r) for r in result_parts)) if result_parts else ''

        if result:
            if prefix:
                return NO_ERR_RESP, False, ((k, '{0}, {1}'.format(prefix, v)) for k, v in result)

            return NO_ERR_RESP, False, result

        if filter_params is not None:
            result = AddrObj.objects.order_by('aolevel').filter(**filter_params)[:30]

            if prefix:
                return (
                    NO_ERR_RESP,
                    False,
                    ((force_unicode(l.pk), '{0}, {1}'.format(prefix, force_unicode(l)), {'level': l.aolevel}) for l in result)
                )
            else:
                return NO_ERR_RESP, False, ((force_unicode(l.pk), force_unicode(l), {'level': l.aolevel}) for l in result)

        return NO_ERR_RESP, False, []
