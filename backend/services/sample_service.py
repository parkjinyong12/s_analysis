from backend.models.sample import Sample
from backend.extensions import db

def create_sample(name, description):
    sample = Sample(name=name, description=description)
    db.session.add(sample)
    db.session.commit()
    return sample

def get_all_samples():
    return Sample.query.all()

def get_sample_by_id(sample_id):
    return Sample.query.get(sample_id)

def update_sample(sample_id, name, description):
    sample = Sample.query.get(sample_id)
    if sample:
        sample.name = name
        sample.description = description
        db.session.commit()
    return sample

def delete_sample(sample_id):
    sample = Sample.query.get(sample_id)
    if sample:
        db.session.delete(sample)
        db.session.commit()
    return sample 