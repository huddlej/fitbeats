import sys
sys.path.append('../')

from django.db import models
from django.db.models import permalink
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from functions import bezier

TRAJECTORY_TYPES = (
                    ('coordinate', 'Coordinate'),
                    ('boolean', 'Boolean'),
                    ('integer', 'Integer'),
                    ('float', 'Float'),
                    )

class Parameter(models.Model):
    name = models.CharField(maxlength=100, editable=False)
    value = models.FloatField()

    def __str__(self):
        return "%s: %f" % (self.name, self.value)

    class Admin:
        search_fields = ['name']

class Crossover(models.Model):
    # TODO: Crossover could implement __call__ and use __import__ to execute
    # the right method.
    name = models.CharField(maxlength=100)
    
    def __str__(self):
        return self.name

    def __repr__(self):
        return "".join((self.name.replace(" ", ""), self.__class__.__name__))

    def get_short_name(self):
        return repr(self)

    class Admin:
        pass

class Selector(models.Model):
    name = models.CharField(maxlength=100)
    parameters = models.ManyToManyField(Parameter, blank=True)
    
    def __str__(self):
        return self.name

    def get_short_name(self):
        return "%s%s" % (self.name.replace(" ", ""), self.__class__.__name__)

    class Admin:
        pass

class Mutator(models.Model):
    name = models.CharField(maxlength=100)
    mutate_all_rows = models.BooleanField(help_text="""Whether this mutator 
                                          should mutate all instrument rows or 
                                          just a randomly selected row.""")

    def __str__(self):
        return "%s%s" % (self.name, self.mutate_all_rows and " (all rows)" or "")

    def get_short_name(self):
        return "%s%s%s" % (self.name.replace(" ", ""), self.mutate_all_rows and "AllRows" or "", self.__class__)

    class Admin:
        pass

    class Meta:
        ordering = ('name', 'mutate_all_rows')

class Instrument(models.Model):
    CATEGORY_CHOICES = (
                    ('L', 'Low'),
                    ('M', 'Mid'),
                    ('H', 'High'),
                    )

    name = models.CharField(maxlength=200)
    category = models.CharField(maxlength=50, choices=CATEGORY_CHOICES)
    sequence_number = models.IntegerField()
    
    def __str__(self):
        return "%i: %s (%s)" % (self.sequence_number, self.name, self.category)

    class Admin:
        pass

    class Meta:
        ordering = ('sequence_number',)

class Pattern(models.Model):
    DEFAULT_VALUES = {
        'gene': {
            'mutation_probability': 0.02,
        },
        'organism': {
            'mutation_probability': 0.02,
            'crossover_rate': 0.6,
        },
        'population': {
            'max_generations': 50,
            'initial_size': 1000,
            'new_children': 200,
        }        
    }

    length = models.IntegerField(help_text="The number of beats in this pattern.")
    instruments = models.ManyToManyField(Instrument)
    selector = models.ForeignKey(Selector, help_text="Determines how fit patterns will be selected.")
    crossover = models.ForeignKey(Crossover, help_text="Determines how individuals will reproduce.")
    mutators = models.ManyToManyField(Mutator, help_text="Introduces random diversity to the population.")
    parameters = models.ManyToManyField(Parameter, editable=False)
    author = models.ForeignKey(User, editable=False)

    def save(self):
        # Create parameters for new patterns
        if self.id and self.parameters.count() == 0:
            for key in self.DEFAULT_VALUES.keys():
                for name in self.DEFAULT_VALUES[key].keys():
                    p = Parameter(name="%s_%s" % (key, name), 
                                  value=self.DEFAULT_VALUES[key][name])
                    p.save()
                    self.parameters.add(p)
        super(Pattern, self).save()
    
    def get_absolute_url(self):
        return ('fitbeats.views.edit_pattern', [str(self.id)])
    get_absolute_url = permalink(get_absolute_url)

    def __str__(self):
        return "Pattern %i (%ix%i, %s, %s)" % (self.id, 
                                          self.length,
                                          self.instrument_length,
                                          self.selector,
                                          self.crossover)
    
    def _instrument_length(self):
        if self.id:
            return self.instruments.count()
        else:
            return 0
    instrument_length = property(_instrument_length)
    
    def get_max_generations(self):
        return 50
    
    class Admin:
        list_display = ['id', 'author', 'length', 'instrument_length', 'selector', 'crossover']

class FitnessFunction(models.Model):
    name = models.CharField(maxlength=100)
    display_name = models.CharField(maxlength=100)
    trajectory_type = models.CharField(maxlength=10, choices=TRAJECTORY_TYPES)
    
    def __str__(self):
        return self.display_name or self.name

    class Admin:
        pass

    class Meta:
        verbose_name = "Fitness rule"
        verbose_name_plural = "Fitness rules"

class FitnessTrajectory(models.Model):
    pattern = models.ForeignKey(Pattern, editable=False)
    function = models.ForeignKey(FitnessFunction, verbose_name="Rhythmic rule")
    trajectory_type = models.CharField(maxlength=10, choices=TRAJECTORY_TYPES, editable=False)
    
    def __str__(self):
        return "%s (%s)" % (self.function, self.trajectory_type)

    def _trajectory_set(self):
        if self.trajectory_type == "coordinate":
            return self.fitnesstrajectorycoordinate_set.order_by('sequence_number')
        elif self.trajectory_type == "boolean":
            return self.fitnesstrajectoryboolean_set.order_by('instrument')
        elif self.trajectory_type == "integer":
            return self.fitnesstrajectoryinteger_set.order_by('instrument')
        elif self.trajectory_type == "float":
            return self.fitnesstrajectoryfloat_set.order_by('instrument')
        else:
            return None
    trajectory_set = property(_trajectory_set)

    def get_absolute_url(self):
        return ('fitbeats.views.edit_trajectory', [str(self.pattern.id), str(self.id)])
    get_absolute_url = permalink(get_absolute_url)

    def calculate_trajectory(self):
        patternLength = self.pattern.length
        
        if self.trajectory_type == "coordinate":
            values = [(v.x, v.y) for v in self.trajectory_set]
            t = 0.0
            self.values = []
        
            # calculate the initial value
            self.values.append(bezier(values[0], 
                                      values[1],
                                      values[2],
                                      values[3],
                                      t))
        
            dt = 1.0 / (patternLength - 1)
            for i in xrange(1, patternLength):
                t += dt
                self.values.append(bezier(values[0], 
                                      values[1],
                                      values[2],
                                      values[3],
                                      t))
        elif self.trajectory_type == "boolean":
            ft_set = self.trajectory_set.order_by('instrument')
            self.values = [i for i in xrange(ft_set.count()) if ft_set[i].value]
        else:
            ft_set = self.trajectory_set.order_by('instrument')
            self.values = [(i, ft_set[i].value) for i in xrange(ft_set.count())]

    class Meta:
        verbose_name_plural = "Fitness trajectories"
        
    class Admin:
        pass

class FitnessTrajectoryCoordinate(models.Model):
    trajectory = models.ForeignKey(FitnessTrajectory, editable=False, null=True)
    sequence_number = models.IntegerField()
    value = models.CharField(maxlength=10, verbose_name="coordinate")
    x = models.FloatField(editable=False)
    y = models.FloatField(editable=False)

    def save(self):
        if self.value.find(",") > 0:
            values = self.value.split(",")
            self.x = float(values[0].strip())
            self.y = float(values[1].strip())
        else:
            self.x, self.y = 0.0, 0.0
        super(FitnessTrajectoryCoordinate, self).save()
    
    def __str__(self):
        return "(%f, %f)" % (self.x, self.y)

    """
    def _value(self):
        return (self.x, self.y)
    value = property(_value)
    """
        
    class Admin:
        pass

class FitnessTrajectoryInteger(models.Model):
    trajectory = models.ForeignKey(FitnessTrajectory, editable=False, null=True)
    instrument = models.ForeignKey(Instrument)
    value = models.IntegerField()
    
    def __str__(self):
        return str(self.value)

    class Admin:
        pass

class FitnessTrajectoryBoolean(models.Model):
    trajectory = models.ForeignKey(FitnessTrajectory, editable=False, null=True)
    instrument = models.ForeignKey(Instrument)
    value = models.BooleanField()
    
    def __str__(self):
        return "%s - %s" % (self.trajectory, str(self.value))

    class Admin:
        pass

class FitnessTrajectoryFloat(models.Model):
    trajectory = models.ForeignKey(FitnessTrajectory, editable=False, null=True)
    instrument = models.ForeignKey(Instrument)
    value = models.FloatField()
    
    def __str__(self):
        return str(self.value)

    class Admin:
        pass

class PatternInstance(models.Model):
    pattern = models.ForeignKey(Pattern, editable=False)
    fitness = models.FloatField()
    value = models.TextField()
    
    class Admin:
        pass

"""
class PatternInstanceComplete:
    length = models.IntegerField(help_text="The number of beats in this pattern.")
    instrument_length = models.IntegerField(editable=False)
    instruments = models.TextField(help_text="Instruments used for this pattern.")
    selector = models.CharField(maxlength=100)
    crossover = models.CharField(maxlength=100)
    mutators = models.CharField(maxlength=250)
    parameters = models.TextField()
    value = models.XMLField(schema_path="")
    author = models.ForeignKey(User)

class Piece(models.Model):
    name = models.CharField(maxlength=150)
    patterns = models.ManyToManyField(Pattern)
    author = models.ForeignKey(User)
"""
