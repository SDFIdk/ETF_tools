class PlotUtils:
    def combine_legends(*axes, location='upper left'):
        """
        Combines legends from multiple axes into a single legend.

        Parameters:
        - *axes: Variable number of matplotlib Axes objects.
        - location (str): Location of the combined legend (default: 'upper left').

        Returns:
        - legend: The combined legend for the provided axes.
        """
        handles = []
        labels = []

        for ax in axes:
            if not ax == None:
                h, l = ax.get_legend_handles_labels()
                handles.extend(h)
                labels.extend(l)

        # Create a single combined legend on the first axis
        if axes and handles and labels:
            return axes[0].legend(handles, labels, loc=location)