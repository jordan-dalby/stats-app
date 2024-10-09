import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

def create_charts(charts_data):
    num_charts = len(charts_data)
    
    fig, axs = plt.subplots(1, num_charts, figsize=(10*num_charts, 7), squeeze=False)
    axs = axs[0]
    
    for i, chart_data in enumerate(charts_data):
        ax = axs[i]
        
        # Decide which type of chart to create
        if chart_data['chart_type'] == 'pie':
            wedges, texts, autotexts = ax.pie(chart_data['sizes'], labels=chart_data['labels'], autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            # Labels
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
        elif chart_data['chart_type'] == 'bar':
            bars = ax.bar(chart_data['labels'], chart_data['sizes'])
            ax.set_ylabel('Value')
            ax.tick_params(axis='x', rotation=45)
            ax.set_xticklabels(chart_data['labels'], ha='right')
            # Labels
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:,.0f}',
                        ha='center', va='bottom')
        elif chart_data['chart_type'] == 'horizontal_bar':
            bars = ax.barh(chart_data['labels'], chart_data['sizes'])
            ax.set_xlabel('Value')
            ax.tick_params(axis='y', rotation=0)
            # Labels
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                        f'{width:,.0f}',
                        ha='left', va='center')
        else:
            raise ValueError(f"Unsupported chart type: {chart_data['chart_type']}")
        
        ax.set_title(chart_data['title'])
    
    plt.tight_layout()
    
    # Save the plot to a bytes buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100)
    buffer.seek(0)
    
    # Encode the image to base64
    image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    plt.close(fig)
    
    return f"data:image/png;base64,{image_base64}"