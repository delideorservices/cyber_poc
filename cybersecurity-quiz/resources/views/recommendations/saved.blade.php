@extends('layouts.app')

@section('content')
<div class="container">
    <div class="row">
        <div class="col-md-12">
            <h1>{{ __('Saved Recommendations') }}</h1>
            
            @if(isset($savedItems) && count($savedItems) > 0)
                <div class="saved-recommendations">
                    @foreach($savedItems as $item)
                        <div class="saved-item" id="saved-{{ $item->id }}">
                            <div class="card mb-3">
                                <div class="card-body">
                                    <h4 class="card-title">{{ $item->title }}</h4>
                                    
                                    @if(isset($item->type) && $item->type)
                                        <div class="recommendation-type">
                                            <span class="badge badge-info">{{ $item->type_label }}</span>
                                        </div>
                                    @endif
                                    
                                    <p class="card-text mt-2">{{ $item->description }}</p>
                                    
                                    <div class="saved-actions mt-3">
                                        @if(isset($item->url) && $item->url)
                                            <a href="{{ $item->url }}" class="btn btn-primary mr-2">
                                                {{ __('View') }}
                                            </a>
                                        @endif
                                        
                                        <button type="button" class="btn btn-outline-danger remove-saved"
                                               data-recommendation-id="{{ $item->id }}">
                                            {{ __('Remove') }}
                                        </button>
                                    </div>
                                </div>
                                <div class="card-footer text-muted">
                                    {{ __('Saved on') }}: {{ $item->saved_at->format('F j, Y') }}
                                </div>
                            </div>
                        </div>
                    @endforeach
                </div>
            @else
                <div class="alert alert-info">
                    {{ __('You haven\'t saved any recommendations yet.') }}
                </div>
                <a href="{{ route('recommendations.index') }}" class="btn btn-primary">
                    {{ __('Browse Recommendations') }}
                </a>
            @endif
        </div>
    </div>
</div>
@endsection

@push('scripts')
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Handle remove saved recommendation
        const removeButtons = document.querySelectorAll('.remove-saved');
        if (removeButtons.length > 0) {
            removeButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const recommendationId = this.getAttribute('data-recommendation-id');
                    const savedItem = document.getElementById(`saved-${recommendationId}`);
                    
                    if (confirm('{{ __("Are you sure you want to remove this saved recommendation?") }}')) {
                        // AJAX call to remove from saved list
                        fetch(`/recommendations/saved/remove/${recommendationId}`, {
                            method: 'DELETE',
                            headers: {
                                'Content-Type': 'application/json',
                                'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
                            }
                        })
                        .then(response => response.json())
                        .then(data => {
                            if (data.success) {
                                savedItem.remove();
                                
                                // Check if there are no saved items left
                                const remainingSavedItems = document.querySelectorAll('.saved-item');
                                if (remainingSavedItems.length === 0) {
                                    // Reload the page to show the empty state
                                    window.location.reload();
                                }
                            } else {
                                alert('{{ __("Failed to remove item. Please try again.") }}');
                            }
                        })
                        .catch(error => {
                            console.error('Error:', error);
                            alert('{{ __("An error occurred. Please try again.") }}');
                        });
                    }
                });
            });
        }
    });
</script>
@endpush