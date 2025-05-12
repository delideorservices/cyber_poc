
<?php
/**
 * Peer Comparison Component
 * 
 * Displays how the user's performance compares to peers
 * 
 * Props:
 * - data: Peer comparison data
 */
?>

<div class="bg-white p-4 rounded-lg shadow-md">
    <h3 class="text-lg font-semibold mb-4">{{ $title ?? 'How You Compare to Peers' }}</h3>
    
    @if(isset($data['status']) && $data['status'] == 'insufficient_data')
        <div class="text-center py-4">
            <p class="text-gray-500">{{ $data['message'] ?? 'Not enough peer data available for comparison.' }}</p>
        </div>
    @else
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
                <thead>
                    <tr>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Skill</th>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Your Score</th>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Peer Average</th>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Percentile</th>
                        <th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    @foreach($data['skill_comparison'] as $comparison)
                        @php
                            $statusClass = match(true) {
                                $comparison['differential'] >= 10 => 'text-green-600',
                                $comparison['differential'] <= -10 => 'text-red-600',
                                default => 'text-yellow-600'
                            };
                            
                            $statusText = match(true) {
                                $comparison['differential'] >= 10 => 'Ahead',
                                $comparison['differential'] <= -10 => 'Behind',
                                default => 'On Par'
                            };
                        @endphp
                        
                        <tr>
                            <td class="px-4 py-3 text-sm font-medium text-gray-900">{{ $comparison['skill_name'] }}</td>
                            <td class="px-4 py-3 text-sm text-gray-900">{{ number_format($comparison['user_score'], 1) }}%</td>
                            <td class="px-4 py-3 text-sm text-gray-900">{{ number_format($comparison['peer_average'], 1) }}%</td>
                            <td class="px-4 py-3 text-sm text-gray-900">{{ number_format($comparison['percentile'], 1) }}</td>
                            <td class="px-4 py-3 text-sm {{ $statusClass }} font-medium">{{ $statusText }}</td>
                        </tr>
                    @endforeach
                </tbody>
            </table>
        </div>
        
        <p class="text-xs text-gray-500 mt-3">Based on comparison with {{ $data['peer_count'] }} peers in your sector and role.</p>
    @endif
</div>