from django.shortcuts import render
import traceback


# Handle return 404 error when users do not find destination page
def page_not_found(request, exception):
    return render(request, "portals/404.html", status=404)


# Handle return 500 error when system catch any error
def page_server_error_500(request):
    error_message = traceback.format_exc()

    return render(
        request,
        "portals/500.html",
        {"error_message": error_message},
        status=500,
    )
