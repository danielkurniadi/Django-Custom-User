from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model

from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import DutySerializer
from .models import (
    Duty, DutyManager,
    CannotStartOverOngoingDuty,
    CannotClearUnfinishedDuty,
)

User = get_user_model()

def get_user_duty(user):
    try:
        return user.duty
    except Duty.DoesNotExist:
        return None

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes((IsAuthenticated, ))
def duty_handler(request):
    user = request.user
    duty_manager = DutyManager.instance

    #############################################
    ## Duty Start
    #############################################

    # POST
    if request.method == 'POST':
        try:
            user = User.objects.get(email=user.email)
            duty_manager.start_duty(user=user)
        except CannotStartOverOngoingDuty as e:
            return Response(
                {
                    'success': False,
                    'message': e.message,
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        else:
            serializer = DutySerializer(duty_manager.duty)
            return Response(
                {
                    'success': True,
                    'message': "%s created sucessfully" % duty_manager.duty,
                    'payload': serializer.data
                }, 
                status=status.HTTP_201_CREATED
            )

    #############################################
    ## Duty Ongoing
    #############################################

    # Http401 if no ongoing duty for that user.
    if not get_user_duty(user):
        return Response(
            {
                'success': False, 
                'message': "User has no ongoing duty at the moment."
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    # Http500 when expired duty not deleted,
    # if this happen please fix TODO: handle & delete expired duty
    if (user != duty_manager.user):
        return Response(
            {
                'success': False, 
                'message': "User's duty is expired but not deleted. Request.user %s; Manager.user %s" 
                    % (user.email, duty_manager.user.email)
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    # GET
    if request.method == 'GET':
        duty = duty_manager.duty
        serializer = DutySerializer(duty)
        return Response(
            {
                'success': True,
                'message': "%s sent" % duty,
                'payload': serializer.data
            },
            status=status.HTTP_200_OK
        )

    # DELETE
    elif request.method == 'DELETE':
        duty_str = duty_manager.duty.__str__()
        try:
            duty_manager.clear_duty()
        except CannotClearUnfinishedDuty as e:
            return Response(
                {
                    'success': False, 
                    'message': e.message,
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            return Response(
                {
                    'success': True,
                    'message': "Duty deactivated.",
                    'payload': duty_str
                }
            )
