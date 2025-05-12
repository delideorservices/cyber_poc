<?php
/**
 * Skill Radar Chart Component
 * 
 * Displays user's skill proficiency compared to peers in a radar chart
 * 
 * Props:
 * - chartId: Unique ID for the chart
 * - data: Chart data with labels and datasets
 * - height: Chart height in pixels (optional)
 * - width: Chart width in pixels (optional)
 */
?>

<div class="bg-white p-4 rounded-lg shadow-md">
    <h3 class="text-lg font-semibold mb-4">{{ $title ?? 'Skill Proficiency Overview' }}</h3>
    
    <div style="height: {{ $height ?? '300px' }}; width: {{ $width ?? '100%' }};">
        <canvas id="{{ $chartId }}">
    </div>
    
    @if(isset($description))
        <p class="text-sm text-gray-600 mt-3">{{ $description }}</p>
    @endif

    @push('scripts')
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const ctx = document.getElementById('{{ $chartId }}').getContext('2d');
            const data = @json($data);
            
            new Chart(ctx, {
                type: 'radar',
                data: data,
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        r: {
                            angleLines: {
                                display: true
                            },
                            suggestedMin: 0,
                            suggestedMax: 100,
                            ticks: {
                                stepSize: 20
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            position: 'top',
                        },
                        tooltip: {
                            callbacks: {
                                label: function(context) {
                                    return context.dataset.label + ': ' + context.raw.toFixed(1) + '%';
                                }
                            }
                        }
                    }
                }
            });
        });
    </script>
    @endpush
</div>