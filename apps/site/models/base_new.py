#!/usr/bin/env python
from django.contrib.gis.db import models
from datetime import datetime
from tagging_autocomplete.models import TagAutocompleteField

class Base(models.Model):
    name = 'base'
    name_plural = 'bases'
    class Meta:
        app_label = 'site'
        abstract = True

    '''
    @property
    def model_name(self):
        return self._meta.verbose_name

    @property
    def model_name_plural(self):
        return self._meta.verbose_name_plural
    '''
    
class BaseAudit(Base):
    owner = models.ForeignKey('auth.User',)
    last_updated_by = models.ForeignKey('auth.User', related_name="%(app_label)s_%(class)s_related")
    date_created = models.DateTimeField(default=datetime.now)
    time_stamp = models.DateTimeField(default=datetime.now, db_column='last_updated')
    
    class Meta:
        app_label = 'site'
        abstract = True
        
    
class BaseNamed(BaseAudit):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    tags = TagAutocompleteField(blank=True, null=True)
    
    class Meta:
        app_label = 'site'
        abstract = True

        
class BaseMedia(BaseAudit):
    #source_scan = models.ForeignKey('Scan', blank=True, null=True)
    source_marker = models.ForeignKey('Marker', blank=True, null=True,
                                related_name="+")
    host = models.CharField(max_length=255)
    virtual_path = models.CharField(max_length=255)
    file_name_orig = models.CharField(max_length=255)
    content_type = models.CharField(max_length=50)
    
    class Meta:
        abstract = True
        app_label = 'site'
        
    def to_dict(self, **kwargs):
        raise NotImplementedError
    
    def get_absolute_path(self):
        return settings.FILE_ROOT + self.virtual_path
    
    def absolute_virtual_path(self):
        return absolute_virtual_path_orig(self)
        
    def absolute_virtual_path_orig(self):
        return self._encrypt_media_path(self.virtual_path + self.file_name_orig)
        
    def save_upload(self, *args, **kwargs):
        raise NotImplementedError
    
    def generate_relative_path(self):
        return '/%s/media/%s/%s/' % (settings.USER_MEDIA_DIR, self.owner.username,
                                                 self._meta.verbose_name_plural)
        
    def generate_absolute_path(self):
        return '%s/media/%s/%s' % (settings.USER_MEDIA_ROOT, self.owner.username,
                                                self._meta.verbose_name_plural)
        
class BaseNamedMedia(BaseMedia):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    tags = TagAutocompleteField(blank=True, null=True)
    
    class Meta:
        app_label = 'site'
        abstract = True
        
class BaseUploadedMedia(BaseNamedMedia):
    file_name_new = models.CharField(max_length=255)
    project = models.ForeignKey('Project')
    attribution = models.CharField(max_length=500, blank=True,
                                   null=True, verbose_name="Author / Creator")
    
    class Meta:
        abstract = True
        app_label = 'site'
        
    def absolute_virtual_path(self):
        return self._encrypt_media_path(self.virtual_path + self.file_name_new)
        
    def _encrypt_media_path(self, path, host=None):
        if host is None:
            host = self.host
            #host = 'dev.localground.org' #for debugging
        from django.http import HttpResponse
        #return path
        return 'http://%s/profile/%s/%s/' % (host, self.model_name_plural, base64.b64encode(path))
         
    def make_directory(self, path):
        from pwd import getpwnam
        os.makedirs(path) #create new directory
        #get OS ids:
        uid = getpwnam(settings.USER_ACCOUNT).pw_uid
        gid = getpwnam(settings.GROUP_ACCOUNT).pw_gid
        #os.chown(path, uid, gid);
        #need to "or" permissions flags together:
        permissions = stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH
        os.chmod(path, permissions)
        
    def save_file_to_disk(self, file):
        #create directory if it doesn't exist:
        media_path = self.generate_absolute_path()
        if not os.path.exists(media_path):
            self.make_directory(media_path)
        
        #derive file name:
        file_name, ext = os.path.splitext(file.name.lower())
        file_name = ''.join(char for char in file_name if char.isalnum()).lower()
        if os.path.exists(media_path + '/%s%s' % (file_name, ext)):
            from time import time
            seconds = int(time())
            file_name = '%s_%s' % (file_name, seconds)
        file_name_new = '%s%s' % (file_name, ext)    
        
        #write request file stream to disk:
        destination     = open(media_path + '/' + file_name_new, 'wb+')
        for chunk in file.chunks():
            destination.write(chunk)
        destination.close()
        return file_name_new
    
    def get_object_type(self):
        return self._meta.verbose_name
    
    def can_view(self, user, access_key=None):
        return self.project.can_view(user, access_key=access_key)
    
    def can_edit(self, user):
        return True
    
    def can_manage(self, user):
        return True
    
    @staticmethod
    def get_cls(object_type):
        if object_type == ObjectTypes.AUDIO:
            from localground.apps.site.models import Audio
            return Audio, ReturnCodes.SUCCESS
        elif object_type == ObjectTypes.PHOTO:
            from localground.apps.site.models import Photo
            return Photo, ReturnCodes.SUCCESS
        elif object_type == ObjectTypes.VIDEO: 
            from localground.apps.site.models import Video
            return Video, ReturnCodes.SUCCESS    
        elif object_type == ObjectTypes.MARKER:
            from localground.apps.site.models import Marker
            return Marker, ReturnCodes.SUCCESS
        elif object_type == ObjectTypes.PRINT:
            from localground.apps.site.models import Print  
            return Print, ReturnCodes.SUCCESS    
        elif object_type.find('table') != -1: 
            #a bit more complicated b/c the Form object is a wrapper for any
            #dynamic table; need to query for the form and for the record:
            from localground.apps.site.models import Form
            form = Form.objects.get(id=object_type.split('_')[1])
            return form.TableModel, ReturnCodes.SUCCESS
        else:
            return None, ReturnCodes.OBJECT_TYPE_DOES_NOT_EXIST
    
    @staticmethod
    def get_instance(object_id, object_type, identity, access_key=None):
        obj = None
        cls, return_code = BaseUploadedMedia.get_cls(object_type)
        if return_code == ReturnCodes.SUCCESS:
            try:
                obj = cls.objects.get(id=object_id)
                if obj.can_view(identity, access_key=access_key):
                    return obj, ReturnCodes.SUCCESS
                else:
                    return None, ReturnCodes.UNAUTHORIZED
            except cls.DoesNotExist:
                return obj, ReturnCodes.OBJECT_DOES_NOT_EXIST
        else:
            return None, return_code
        
    @staticmethod
    def create_instance(object_type, user, project, *args, **kwargs):
        cls, return_code = BaseUploadedMedia.get_cls(object_type)
        if return_code == ReturnCodes.SUCCESS:
            return cls.create_instance(user, project, *args, **kwargs)
        else:
            return None, return_code
        
    @staticmethod 
    def update_instance(object_id, object_type, identity, update_dictionary):
        object, return_code = BaseUploadedMedia.get_instance(object_id, object_type, identity)
        if return_code != ReturnCodes.SUCCESS:
            return None, return_code
        if object.can_edit(identity):
            d = update_dictionary
            for k, v in d.items():
                object.__setattr__(k, v)
            object.time_stamp = datetime.now()
            object.last_updated_by = identity
            object.save()
        else:
            return None, ReturnCodes.UNAUTHORIZED
        return object, ReturnCodes.SUCCESS
    
    @staticmethod 
    def delete_instance(object_id, object_type, identity):
        object, return_code = BaseUploadedMedia.get_instance(object_id, object_type, identity)
        if return_code != ReturnCodes.SUCCESS:
            return return_code
        if object.can_edit(identity):
            object.delete()
        else:
            return ReturnCodes.UNAUTHORIZED
        return ReturnCodes.SUCCESS
        
    def delete(self, *args, **kwargs):
        self.clear_nullable_related(*args, **kwargs)
        super(BaseUploadedMedia, self).delete(*args, **kwargs)

    def clear_nullable_related(self, *args, **kwargs):
        """
        Recursively clears any nullable foreign key fields on related objects.
        Django is hard-wired for cascading deletes, which is very dangerous for
        us. This simulates ON DELETE SET NULL behavior manually.
        """
        for related in self._meta.get_all_related_objects():
            accessor = related.get_accessor_name()
            related_set = getattr(self, accessor)

            if related.field.null:
                related_set.clear()
            else:
                for related_object in related_set.all():
                    #careful - recursion here:
                    try:
                        related_object.clear_nullable_related()
                    except:
                        #not all child objects have a clear_nullabe_related()
                        #method
                        pass
    
class BasePoint(Base):
    """
    abstract class for uploads with lat/lng references.
    """
    point = models.PointField(blank=True, null=True)
    
    class Meta:
        abstract = True
    
    def display_coords(self):
        if self.point is not None:
            try:
                return '(%0.4f, %0.4f)'  % (self.point.y, self.point.x)
            except ValueError:
                return 'String Format Error: (%s, %s)' % (str(self.point.y), str(self.point.x))
        return '(?, ?)'
    
    def update_latlng(self, lat, lng, user):
        '''Tries to update lat/lng, returns code'''
        from django.contrib.gis.geos import Point
        try:
            if self.can_edit(user):
                self.point = Point(lng, lat, srid=4326)
                self.last_updated_by = user
                self.save()
                return ReturnCodes.SUCCESS
            else:
                return ReturnCodes.UNAUTHORIZED
        except Exception:
            return ReturnCodes.UNKNOWN_ERROR
    
    def remove_latlng(self, user):
        try:
            if self.can_edit(user):
                self.point = None
                self.last_updated_by = user
                self.save()
                return ReturnCodes.SUCCESS
            else:
                return ReturnCodes.UNAUTHORIZED
        except Exception:
            return ReturnCodes.UNKNOWN_ERROR
    
    def __unicode__(self):
        return self.display_coords()
        

class BaseExtents(Base):
    """
    abstract class for uploads with lat/lng references.
    """
    extents = models.PolygonField()
    northeast = models.PointField()
    southwest = models.PointField()
    center = models.PointField()
    zoom = models.IntegerField()
    
    class Meta:
        abstract = True
    
    def display_coords(self):
        if self.point is not None:
            try:
                return '(%0.4f, %0.4f)'  % (self.point.y, self.point.x)
            except ValueError:
                return 'String Format Error: (%s, %s)' % (str(self.point.y), str(self.point.x))
        return '(?, ?)'
    
    def update_latlng(self, lat, lng, user):
        '''Tries to update lat/lng, returns code'''
        from django.contrib.gis.geos import Point
        try:
            if self.can_edit(user):
                self.point = Point(lng, lat, srid=4326)
                self.last_updated_by = user
                self.save()
                return ReturnCodes.SUCCESS
            else:
                return ReturnCodes.UNAUTHORIZED
        except Exception:
            return ReturnCodes.UNKNOWN_ERROR
    
    def remove_latlng(self, user):
        try:
            if self.can_edit(user):
                self.point = None
                self.last_updated_by = user
                self.save()
                return ReturnCodes.SUCCESS
            else:
                return ReturnCodes.UNAUTHORIZED
        except Exception:
            return ReturnCodes.UNKNOWN_ERROR
    
    def __unicode__(self):
        return self.display_coords()
        
class StatusCode(models.Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=2000, null=True, blank=True)
    def __unicode__(self):
        return str(self.id) + ': ' + self.name
        
    class Meta:
        app_label = 'site'

class UploadSource(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return str(self.id) + '. ' + self.name
        
    class Meta:
        app_label = 'site'
        
class UploadType(models.Model):
    name = models.CharField(max_length=255)
    def __unicode__(self):
        return str(self.id) + '. ' + self.name
    
    class Meta:
        app_label = 'site'
        
class ErrorCode(models.Model):
    name                  = models.CharField(max_length=255)
    description           = models.CharField(max_length=2000, null=True, blank=True)
    def __unicode__(self):
        return str(self.id) + ': ' + self.name
        
    class Meta:
        app_label = 'site'


