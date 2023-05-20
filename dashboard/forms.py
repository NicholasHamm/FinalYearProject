from django import forms


class SelectCurrentForm(forms.Form):
    """ Class to sanitize data for selecting current datacenter
        from the Home tab
    """

    current_datacenter = forms.CharField(required=False)

    def clean_current_datacenter(self):
        data = self.cleaned_data['current_datacenter']
        return data


class UpdateDatacenterForm(forms.Form):
    update = forms.CharField(required=False)

    def clean_update(self):
        data = self.cleaned_data['update']
        return data

class RefreshGraphsForm(forms.Form):
    refresh = forms.CharField(required=False)

    def clean_update(self):
        data = self.cleaned_data['refresh']
        return data


class DeleteConfigurationForm(forms.Form):
    """ Class to sanitize data for deleting selected datacenter
        from the Home tab
    """

    to_delete = forms.CharField(required=True)

    def clean_current_datacenter(self):
        data = self.cleaned_data['to_delete']
        return data


class ChangeThresholdForm(forms.Form):
    """ Class to sanitize data for changing threshold in the 
        Assets/ Racks/ Hosts tab
    """

    low = forms.CharField(required=True)
    medium = forms.CharField(required=True)

    def clean(self):
        low = self.cleaned_data['low']
        medium = self.cleaned_data['medium']

        if float(low) > float(medium):
            raise forms.ValidationError("Upper Threshold must be greater than lower")

        if float(low) < 0 or float(low) > 100:
            raise forms.ValidationError("Lower Threshold must be between 0 and 100")

        if float(medium) < 0 or float(medium) > 100:
            raise forms.ValidationError("Upper Threshold must be between 0 and 100")

        return float(low), float(medium)


class ChangeIPForm(forms.Form):
    """ Class to sanitize data for changing IP in the 
        Home tab
    """

    ip = forms.CharField(required=True)

    def clean(self):
        data = self.cleaned_data['ip']
        return data


class ConfigureNewDatacenterForm(forms.Form):
    """ Class to sanitize data for creating new datacenter
        in the Home tab
    """

    to_configure = forms.CharField(required=True)
    start = forms.DateField(required=True)
    endTime = forms.DateField(required=False)
    pue = forms.FloatField(required=True)
    # energy_cost = forms.FloatField(required=True)
    # carbon_conversion = forms.FloatField(required=True)

    def clean(self):
        to_configure = self.cleaned_data['to_configure']
        start = self.cleaned_data['start']
        end = self.cleaned_data['endTime']
        pue = self.cleaned_data['pue']

        if start == None:
            raise forms.ValidationError("You must include a start date")

        if end != None:
            if end <= start:
                raise forms.ValidationError("Start date must be before end date")

        if pue <= 0 or pue >= 3:
            raise forms.ValidationError("PUE must be between 1 and 3")

        return to_configure, start, end, pue


class CalculateTCOForm(forms.Form):
    """ Class to sanitize data for calculating TCO in the 
        TCO tab
    """

    capital = forms.IntegerField(required=True)
    rack = forms.CharField(required=True)
    floor = forms.CharField(required=False)
    host = forms.CharField(required=True)

    def clean(self):
        capital = self.cleaned_data['capital']
        rack = self.cleaned_data['rack']
        floor = self.cleaned_data['floor']
        host = self.cleaned_data['host']

        if capital <= 0 or capital >= 2147483647:
            raise forms.ValidationError("Capital must be a positive number")

        return capital, rack, floor, host

class ChangeFlexibilityForm(forms.Form):
    hostid = forms.IntegerField(required=True)
    floorid = forms.IntegerField(required=True)
    rackid = forms.IntegerField(required=True)

    def clean(self):
        hostid = self.cleaned_data.get('hostid')
        rackid = self.cleaned_data.get('rackid')
        floorid = self.cleaned_data.get('floorid')
        return int(hostid), int(rackid), int(floorid)

class RefreshGraphsForm(forms.Form):
    refresh = forms.CharField(required=True)

    def clean_update(self):
        data = self.cleaned_data.get('refresh')
        return data


class ChangeTariffForm(forms.Form):
    """ Class to sanitize data for changing threshold in the 
        Assets/ Racks/ Hosts tab
    """

    low = forms.CharField(required=True)
    high = forms.CharField(required=True)

    def clean(self):
        low = self.cleaned_data['low']
        high = self.cleaned_data['high']

        if float(low) > float(high):
            raise forms.ValidationError("High Tariff should be greater than Low Tarriff")

        if float(low) < 0 or float(low) > 100 :
            raise forms.ValidationError("Tariff must be between 0.0 and 100")
        
        if float(high) < 0 or float(high) > 100 :
            raise forms.ValidationError("Tariff must be between 0.0 and 100")

        return float(low), float(high)
