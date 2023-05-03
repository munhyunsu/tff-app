import os
import io
import pickle

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 
import tensorflow as tf
tf.get_logger().setLevel('ERROR')

import model


class FLModel(model.Model):
    def __init__(self, **kwargs):
        self.name = 'CNN-CaltechFC'
        self.label = ['acadian_flycatcher', 'american_crow', 'american_goldfinch', 'american_pipit', 'american_redstart', 'american_three_toed_woodpecker', 'anna_hummingbird', 'artic_tern', 'baird_sparrow', 'baltimore_oriole', 'bank_swallow', 'barn_swallow', 'bay_breasted_warbler', 'belted_kingfisher', 'bewick_wren', 'black_and_white_warbler', 'black_billed_cuckoo', 'black_capped_vireo', 'black_footed_albatross', 'black_tern', 'black_throated_blue_warbler', 'black_throated_sparrow', 'blue_grosbeak', 'blue_headed_vireo', 'blue_jay', 'blue_winged_warbler', 'boat_tailed_grackle', 'bobolink', 'bohemian_waxwing', 'brandt_cormorant', 'brewer_blackbird', 'brewer_sparrow', 'bronzed_cowbird', 'brown_creeper', 'brown_pelican', 'brown_thrasher', 'cactus_wren', 'california_gull', 'canada_warbler', 'cape_glossy_starling', 'cape_may_warbler', 'cardinal', 'carolina_wren', 'caspian_tern', 'cedar_waxwing', 'cerulean_warbler', 'chestnut_sided_warbler', 'chipping_sparrow', 'chuck_will_widow', 'clark_nutcracker', 'clay_colored_sparrow', 'cliff_swallow', 'common_raven', 'common_tern', 'common_yellowthroat', 'crested_auklet', 'dark_eyed_junco', 'downy_woodpecker', 'eared_grebe', 'eastern_towhee', 'elegant_tern', 'european_goldfinch', 'evening_grosbeak', 'field_sparrow', 'fish_crow', 'florida_jay', 'forsters_tern', 'fox_sparrow', 'frigatebird', 'gadwall', 'geococcyx', 'glaucous_winged_gull', 'golden_winged_warbler', 'grasshopper_sparrow', 'gray_catbird', 'gray_crowned_rosy_finch', 'gray_kingbird', 'great_crested_flycatcher', 'great_grey_shrike', 'green_jay', 'green_kingfisher', 'green_tailed_towhee', 'green_violetear', 'groove_billed_ani', 'harris_sparrow', 'heermann_gull', 'henslow_sparrow', 'herring_gull', 'hooded_merganser', 'hooded_oriole', 'hooded_warbler', 'horned_grebe', 'horned_lark', 'horned_puffin', 'house_sparrow', 'house_wren', 'indigo_bunting', 'ivory_gull', 'kentucky_warbler', 'laysan_albatross', 'lazuli_bunting', 'le_conte_sparrow', 'least_auklet', 'least_flycatcher', 'least_tern', 'lincoln_sparrow', 'loggerhead_shrike', 'long_tailed_jaeger', 'louisiana_waterthrush', 'magnolia_warbler', 'mallard', 'mangrove_cuckoo', 'marsh_wren', 'mockingbird', 'mourning_warbler', 'myrtle_warbler', 'nashville_warbler', 'nelson_sharp_tailed_sparrow', 'nighthawk', 'northern_flicker', 'northern_fulmar', 'northern_waterthrush', 'olive_sided_flycatcher', 'orange_crowned_warbler', 'orchard_oriole', 'ovenbird', 'pacific_loon', 'painted_bunting', 'palm_warbler', 'parakeet_auklet', 'pelagic_cormorant', 'philadelphia_vireo', 'pied_billed_grebe', 'pied_kingfisher', 'pigeon_guillemot', 'pileated_woodpecker', 'pine_grosbeak', 'pine_warbler', 'pomarine_jaeger', 'prairie_warbler', 'prothonotary_warbler', 'purple_finch', 'red_bellied_woodpecker', 'red_breasted_merganser', 'red_cockaded_woodpecker', 'red_eyed_vireo', 'red_faced_cormorant', 'red_headed_woodpecker', 'red_legged_kittiwake', 'red_winged_blackbird', 'rhinoceros_auklet', 'ring_billed_gull', 'ringed_kingfisher', 'rock_wren', 'rose_breasted_grosbeak', 'ruby_throated_hummingbird', 'rufous_hummingbird', 'rusty_blackbird', 'sage_thrasher', 'savannah_sparrow', 'sayornis', 'scarlet_tanager', 'scissor_tailed_flycatcher', 'scott_oriole', 'seaside_sparrow', 'shiny_cowbird', 'slaty_backed_gull', 'song_sparrow', 'sooty_albatross', 'spotted_catbird', 'summer_tanager', 'swainson_warbler', 'tennessee_warbler', 'tree_sparrow', 'tree_swallow', 'tropical_kingbird', 'vermilion_flycatcher', 'vesper_sparrow', 'warbling_vireo', 'western_grebe', 'western_gull', 'western_meadowlark', 'western_wood_pewee', 'whip_poor_will', 'white_breasted_kingfisher', 'white_breasted_nuthatch', 'white_crowned_sparrow', 'white_eyed_vireo', 'white_necked_raven', 'white_pelican', 'white_throated_sparrow', 'wilson_warbler', 'winter_wren', 'worm_eating_warbler', 'yellow_bellied_flycatcher', 'yellow_billed_cuckoo', 'yellow_breasted_chat', 'yellow_headed_blackbird', 'yellow_throated_vireo', 'yellow_warbler']
        self.model = tf.keras.models.Sequential([
                       tf.keras.layers.Conv2D(32, (3, 3), activation='relu', input_shape=(32, 32, 3)),
                       tf.keras.layers.MaxPooling2D((2, 2)),
                       tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                       tf.keras.layers.MaxPooling2D((2, 2)),
                       tf.keras.layers.Conv2D(64, (3, 3), activation='relu'),
                       tf.keras.layers.Flatten(),
                       tf.keras.layers.Dense(64, activation='relu'),
                       tf.keras.layers.Dense(len(self.label))])
        fork_model = tf.keras.models.load_model('/home/harny/Github/tff-app/2021-TBD/models/cifar10f/v0.0.51')
        for i in range(len(fork_model.layers)-1):
            self.model.layers[i].set_weights(fork_model.layers[i].get_weights())
        self.compile_ = {'optimizer': 'tf.keras.optimizers.Adam()',
                         'loss': 'tf.keras.losses.CategoricalCrossentropy(from_logits=True)',
                         'metrics': "['accuracy']"}

    def get_name(self):
        return self.name

    def get_compile(self):
        compile_bytes = io.BytesIO()
        pickle.dump(self.compile_, compile_bytes)
        compile_bytes.seek(0)
        return compile_bytes.getvalue()

    def get_label(self):
        labels_bytes = io.BytesIO()
        pickle.dump(self.label, labels_bytes)
        labels_bytes.seek(0)
        return labels_bytes.getvalue()

    def get_architecture(self):
        return self.model.to_json()

    def get_parameter(self):
        weights_bytes = io.BytesIO()
        pickle.dump(self.model.get_weights(), weights_bytes)
        weights_bytes.seek(0)
        return weights_bytes.getvalue()

