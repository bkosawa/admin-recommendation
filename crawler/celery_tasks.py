from celery.utils.log import get_task_logger

from admin_recommendation.celery import app
from crawler.models import App, UserApps, SimilarApp, User

logger = get_task_logger('celery.tasks')


@app.task(name='recommend_to_user')
def recommend_to_user(user_id):
    logger.info("Finding user: {}".format(user_id))
    user = User.objects.get(id=user_id)
    if not user:
        logger.info("No user found")
        return

    logger.info("User found: {}".format(user))
    logger.info("Finding user apps")
    user_apps = UserApps.objects.filter(user=user).all()
    apps = set()
    if not user_apps:
        logger.info("No user apps found")
        return

    for user_app in user_apps:
        package_name = user_app.package_name
        logger.info("Finding similar to {}".format(package_name))
        similar_apps = SimilarApp.objects.filter(source_package=package_name).all()
        for similar_app in similar_apps:
            similar_app_package = similar_app.similar_package
            app_similar = App.objects.filter(package_name=similar_app_package).first()
            if app_similar:
                logger.info("Similar to {} found: {}".format(package_name, app_similar.package_name))
                apps.add(app_similar)

        other_similar_apps = SimilarApp.objects.filter(similar_package=package_name).all()
        for similar_app in other_similar_apps:
            similar_app_package = similar_app.similar_package
            app_similar = App.objects.filter(package_name=similar_app_package).first()
            if app_similar:
                logger.info("Similar to {} found: {}".format(package_name, app_similar.package_name))
                apps.add(app_similar)

    if len(apps) > 0:
        user.recommended_apps = list(apps)
        user.save()
