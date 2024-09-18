from data_table_functions.data_table_utils import DataTableUtils

class MainDataPlot:
    def plot_csv_list(ax1, data_list, data_tag, color_list, style_list, date_range=None, zorder=10):

        for csv_file, metadata in data_list:
            data = DataTableUtils.get_et_csv_data(csv_file, date_range)

            ax1.plot(
                data['date'],
                data[data_tag],
                label=f"{metadata.model} {metadata.adjustment}",
                color=color_list[metadata.color],
                linestyle=style_list[metadata.style],
                zorder=zorder
            )