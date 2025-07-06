import { ResponsivePie } from '@nivo/pie';

function PieChart({ data }) {
    return (
        <div className="result">
            <ResponsivePie
                data={data}
                margin={{ top: 20, right: 20, bottom: 40, left: 20 }}
                padAngle={0.7}
                cornerRadius={3}
                colors={{ scheme: 'nivo' }}
                borderWidth={1}
                borderColor="   #1A1968"
                enableArcLinkLabels={false}
                enableSliceLabels={false}
                arcLabel={d => `${d.id}`}
                arcLabelsSkipAngle={10} 
                arcLabelsTextColor="black"
                theme={{
                    labels: {
                        text: {
                            fill: 'white',
                        },
                    },
                    legends: {
                        text: {
                            fill: 'white',
                        },
                    },
                }}
            />
        </div>
    );
}

export default PieChart;
